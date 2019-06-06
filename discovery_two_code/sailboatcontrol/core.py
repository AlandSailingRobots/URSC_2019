#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import threading
import time

import geojson
import smbus
import csv
import math
import numpy as np
import paho.mqtt.client as mqtt
import pynmea2
import serial
from datetime import datetime
from Adafruit_BNO055 import BNO055
from Adafruit_PCA9685 import PCA9685
from geographiclib.geodesic import Geodesic
from logging.handlers import TimedRotatingFileHandler

try:
    from sailboatcontrol import helpers
except ImportError as e:
    import helpers

abspath = os.path.abspath(__file__)
os.chdir(os.path.dirname(abspath))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-5.5s]  %(message)s',
    handlers=[
        TimedRotatingFileHandler('{0}/{1}'.format('../logs', 'sailboat-control'), encoding='utf-8', when="m", interval=30),
        logging.StreamHandler()
    ]
)

MQTT_HOST = '192.168.4.1'
BNO_SERIAL_PORT = '/dev/serial0'
GPS_SERIAL_PORT = '/dev/ttyACM0'
MS_KN = 1.944
WIND_ANGLE_THRESHOLD_DEGREE = 30
WIND_ANGLE_THRESHOLD_DEGREE_OFFSET = 0
TARGET_RADIUS = 5
PATH_CALCULATION_ITERATIONS = 1
PATH_CALCULATION_TIMEOUT = 0.1
CALIBRATION_THRESHOLD = 1
DIRECT_WIND_OFFSET = 45
GPS_ERROR_TIMEOUT = 2

DEBUG = False
COMPASS = True

# NORTH = 0
# EAST  = 90
# SOUTH = 180
# WEST  = 270
wind_direction = 0
wind_direction_x_y = (90 - wind_direction) % 360
wind_speed = 7.71604938271605
wind_data = False

boat_heading = 0
boat_heading_x_y = 90

gps_thread_stop = threading.Event()
bno_thread_stop = threading.Event()
compass_thread_stop = threading.Event()

gps = {'lon': 0.0, 'lat': 0.0, 'speed': 0.0, 'status': 'V', 'timestamp': datetime.now()}

with open('../json/wind.json') as g:
    wind = json.load(g)


def gps_sensor(s, stop_event):
    global gps
    try:
        with open('../logs/gps.csv', 'a') as gps_log_file:
            csv_writer = csv.writer(gps_log_file)
            while not stop_event.is_set():
                try:
                    line = s.readline().decode('ASCII')
                    msg = pynmea2.parse(line)
                    if msg.sentence_type == 'RMC' and msg.status == 'A':
                        gps['status'] = msg.status
                        gps['lon'] = msg.longitude
                        gps['lat'] = msg.latitude
                        gps['speed'] = kn_to_ms(msg.spd_over_grnd)
                        gps['timestamp'] = datetime.now()
                        csv_writer.writerow([datetime.utcnow().isoformat(), msg.latitude, msg.longitude])
                except Exception as e:
                    logging.warn('ERROR IN GPS THREAD, WAITING {} SECONDS...: {}'.format(GPS_ERROR_TIMEOUT, e))
                    time.sleep(GPS_ERROR_TIMEOUT)
    except Exception as e:
        logging.error('ERROR IN GPS THREAD: {}'.format(e))


def bno_sensor(bno, stop_event):
    global boat_heading, boat_heading_x_y
    try:
        while not stop_event.is_set():
            heading, roll, pitch = bno.read_euler()
            boat_heading = heading
            boat_heading_x_y = (90 - heading) % 360
            time.sleep(0.1)
    except Exception as e:
        logging.error('ERROR IN BNO THREAD: {}'.format(e))

def compass_sensor(compass, stop_event):
    global boat_heading, boat_heading_x_y
    try:
        while not stop_event.is_set():
            boat_heading = (read_compass_bearing(compass) + 180) % 360
            boat_heading_x_y = (90 - boat_heading) % 360
            time.sleep(0.1)
    except Exception as e:
        logging.error('ERROR IN COMPASS THREAD: {}'.format(e))


def read_compass_bearing(bus):
	return ((bus.read_byte_data(0x60, 0x02) << 8) + bus.read_byte_data(0x60, 0x03)) / 10
	

def read_calibration_state(bus):
    value = bus.read_byte_data(0x60, 0x1E)
    mask = 0b00000011
    calibration = [0, 0, 0, 0]
    for i in range(4):
        calibration[3 - i] = (value & mask) >> (2 * i)
        mask = mask << 2
    return calibration


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))
    client.subscribe("weather")


def on_disconnect(client, userdata, rc=0):
    logging.info("Disconnected with result code " + str(rc))
    client.loop_stop()


def on_message(client, userdata, msg):
    global wind_direction, wind_direction_x_y, wind_speed, wind_data
    msg = json.loads(msg.payload.decode('ASCII'))
    wind_direction = msg['direction']
    wind_direction_x_y = (90 - wind_direction) % 360
    wind_speed = msg['speed']
    wind_data = True


def unit_vector(angle):
    return np.array([np.cos(angle), np.sin(angle)])


def angle_between_vectors(v1, v2):
    return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def angle_between_angles(a1, a2):
    return 180 - abs(abs(a1 - a2) - 180)


def get_nearest_value(dictionary, value):
    return min(dictionary, key=lambda x: abs(float(x) - value))


def median(a, b, c):
    return math.sqrt(abs((2 * (a ** 2 + b ** 2) - c ** 2) / 4))


def kn_to_ms(kn):
    return kn / MS_KN


def ms_to_kn(ms):
    return ms * MS_KN


def get_opposite_angle(hypotenuse, cathetus):
    return math.asin(cathetus / hypotenuse)


def get_adjacent_angle(hypotenuse, cathetus):
    return math.acos(cathetus / hypotenuse)


class Vector:
    __vector = None

    def __init__(self, angle, length):
        self.__vector = np.array([np.cos(angle), np.sin(angle)]) * length

    @staticmethod
    def from_vector(vector):
        v = Vector(0, 0)
        v.set_vector(vector)
        return v

    def get_angle(self):
        return math.radians(self.get_angle_degrees())

    def get_vector(self):
        return self.__vector

    def set_vector(self, vector):
        self.__vector = vector

    def set_angle(self, angle):
        self.__init__(angle, self.get_length())

    def get_angle_degrees(self):
        inv = np.arctan2(self.y(), self.x())
        degree = np.mod(np.degrees(inv), 360)
        return degree

    def get_length(self):
        return np.linalg.norm(self.__vector)

    def set_length(self, length):
        self.__init__(self.get_angle(), length)

    def get_adjacent_len(self):
        return math.fabs(math.cos(self.get_angle()) * self.get_length())

    def get_opposite_len(self):
        return math.fabs(math.sin(self.get_angle()) * self.get_length())

    def x(self):
        return self.__vector.item(0)

    def y(self):
        return self.__vector.item(1)

    def __repr__(self):
        return json.dumps({'vector': '[{:.2f}, {:.2f}]'.format(self.__vector[0], self.__vector[1])})


class Path:
    __length = 0
    __time = 0
    __index = -1

    def __init__(self, index, *vectors):
        self.__index = index
        self.__vectors = list(vectors)

    def calculate_vectors(self):
        global WIND_ANGLE_THRESHOLD_DEGREE_OFFSET

        impossible_path = False

        for k, vector in enumerate(self.__vectors):
            if not impossible_path:
                logging.debug('Vector {}: {}'.format(k, vector))
                apparent_wind_angle = angle_between_angles(wind_direction_x_y, vector.get_angle_degrees())

                if apparent_wind_angle < WIND_ANGLE_THRESHOLD_DEGREE + WIND_ANGLE_THRESHOLD_DEGREE_OFFSET:
                    logging.info('Path {}: {} has an impossible angle in Vector: {} {} with {:.2f}°'
                                 .format(self.__index, self, k, vector, apparent_wind_angle))
                    impossible_path = True
                    WIND_ANGLE_THRESHOLD_DEGREE_OFFSET = 10
                else:
                    WIND_ANGLE_THRESHOLD_DEGREE_OFFSET = 0
                    logging.debug('Real wind speed: {:.2f} m/s / {:.2f} kn'.format(wind_speed, ms_to_kn(wind_speed)))
                    logging.debug('Real wind angle in x/y: {:.2f}°'.format(wind_direction_x_y))
                    logging.debug('Boat angle on vector: {:.2f}°'.format(vector.get_angle_degrees()))
                    logging.debug('Apparent wind angle: {:.2f}°'.format(apparent_wind_angle))
                    nearest_wind_speed = float(get_nearest_value(wind['wind'], ms_to_kn(wind_speed)))
                    boat_angle = get_nearest_value(wind['wind'][str(nearest_wind_speed)], apparent_wind_angle)
                    boat_speed = wind['wind'][str(nearest_wind_speed)][boat_angle]
                    boat_speed_ms = kn_to_ms(boat_speed)
                    boat_angle = float(boat_angle)
                    logging.debug('Nearest boat speed on vector {:.2f} m/s / {:.2f} kn'.format(boat_speed_ms, boat_speed))
                    logging.debug('Nearest boat angle on vector: {:.2f}°'.format(boat_angle))
                    self.add_length(vector.get_length())
                    self.add_time(vector.get_length() / boat_speed_ms)
        return impossible_path

    def get_heading(self):
        return self.__vectors[0].get_angle_degrees()

    def get_vectors(self):
        return self.__vectors

    def set_vector(self, index, vector):
        self.__vectors[index] = vector

    def add_vector_prefix(self, vector_prefix):
        self.__vectors.insert(0, vector_prefix)

    def get_length(self):
        return self.__length

    def add_length(self, length):
        self.__length += length

    def get_time(self):
        return self.__time

    def add_time(self, time):
        self.__time += time

    def get_index(self):
        return self.__index

    def __repr__(self):
        return json.dumps(
            {'path': {'length': '{:.2f}'.format(self.__length), 'time': '{:.2f}'.format(self.__time),
                      'vectors': json.loads(str(self.__vectors))}})


def calculate_initial_paths(target_angle, target_distance):
    v1 = Vector(math.radians(target_angle), target_distance)
    v2_a = Vector.from_vector(np.array([v1.x(), 0]))
    v2_b = Vector.from_vector(np.array([0, v1.y()]))
    v3_a = Vector(v2_a.get_angle(), v2_a.get_length() / 2)
    angle = math.degrees(math.atan(v2_b.get_length() / v3_a.get_length())) if v3_a.get_length() > 0 else 0
    x = v1.x()
    y = v1.y()
    if x >= 0:
        if y >= 0:
            angle = angle
        else:
            angle = 360 - angle
    else:
        if y >= 0:
            angle = 180 - angle
        else:
            angle = 180 + angle
    v3_b = Vector(math.radians(angle), median(v1.get_length(), v2_b.get_length(), v2_a.get_length()))

    return [Path(0, v1)] # , Path(1, v2_a, v2_b), Path(2, v3_a, v3_b)]


def calculate_paths(v1, v2, v3, direction):
    v2_a = v2
    v2_b = v3

    v3_a = Vector(v2_a.get_angle(), v2_a.get_length() / 2)
    v3_b_l = median(v1.get_length(), v2_b.get_length(), v2_a.get_length())

    if direction == 'right':
        angle = math.degrees(math.atan(v2_b.get_length() / (abs(v1.x()) - v3_a.get_length()))) if abs(v1.x()) - v3_a.get_length() > 0 else 0
    else:  # direction == left
        angle = math.degrees(math.atan(v2_b.get_length() / v3_a.get_length())) if v3_a.get_length() > 0 else 0

    x = v1.x()
    y = v1.y()
    if x >= 0:
        if y >= 0:
            angle = angle
        else:
            angle = 360 - angle
    else:
        if y >= 0:
            angle = 180 - angle
        else:
            angle = 180 + angle

    v3_b = Vector(math.radians(angle), v3_b_l)

    return [Path(0, v1)] # , Path(1, v2_a, v2_b), Path(2, v3_a, v3_b)]


def calculate_best_path(paths, increments):
    vector_prefix = np.array([0, 0])

    for x in range(increments):
        logging.info('Starting iteration: {}'.format(x + 1))
        impossible_paths = []

        for j, path in enumerate(paths):
            if path.calculate_vectors():
                impossible_paths.append(j)
    
            logging.debug('Path {}: {}'.format(j, path))

        for path in sorted(impossible_paths, reverse=True):
            del paths[path]

        paths.sort(key=lambda p: p.get_time())

        if len(paths) == 0:
            logging.info('No suitable path found. Target is directly in the wind')
            offset = DIRECT_WIND_OFFSET
            if ((boat_heading_x_y - wind_direction_x_y) + 180) % 360 - 180 >= 0:
                offset = offset * 1
            else:
                offset = offset * -1
            paths.append(Path(0, Vector(math.radians((wind_direction_x_y + offset) % 360), 1)))
        if len(paths) == 1:
            return paths[0]
        logging.debug('Sorted paths by time: {}'.format(paths))

        if x + 1 < increments:
            if paths[0].get_index() == 0 or paths[1].get_index() == 0:
                p1, p2 = (paths[0], paths[1]) if paths[0].get_index() == 0 else (paths[1], paths[0])
                v1 = p1.get_vectors()[0]
                v2 = p2.get_vectors()[0]
                v3 = p2.get_vectors()[1]

                paths = calculate_paths(v1, v2, v3, direction='right')
            elif paths[0].get_index() == 1 or paths[1].get_index() == 1:
                p1, p2 = (paths[0], paths[1]) if paths[0].get_index() == 0 else (paths[1], paths[0])
                v1 = p1.get_vectors()[1]
                v2 = p1.get_vectors()[0]
                v3 = p2.get_vectors()[1]

                vector_prefix = np.add(vector_prefix, v2.get_vector())
                paths = calculate_paths(v1, v2, v3, direction='left')

    best_path = paths[0]

    if np.any(vector_prefix):
        first_vector = best_path.get_vectors()[0].get_vector()
        if angle_between_vectors(first_vector, vector_prefix) == 0.0:
            best_path.set_vector(0, Vector(math.radians(90), np.linalg.norm(np.add(first_vector, vector_prefix))))
        else:
            best_path.add_vector_prefix(Vector(math.radians(90), np.linalg.norm(vector_prefix)))
        logging.debug('Updating the best path with the prefix vector')
        best_path.calculate_vectors()

    return best_path

def hold_position():
    global wind_data
    logging.info('Holding position...')
    while True:
        heading_delta = (((wind_direction_x_y - boat_heading_x_y) + 180) % 360 - 180) * -1
        rudder_servo_value = helpers.map_rudder_servo(heading_delta)
        time.sleep(PATH_CALCULATION_TIMEOUT)


def shutdown_routine():
    gps_thread_stop.set()
    bno_thread_stop.set()
    compass_thread_stop.set()
    logging.info('Goodbye :)')
    sys.exit(0)


def main():
    global wind_data
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    if DEBUG:
        wind_data = True
    else:
        client.connect(MQTT_HOST, 1883, 60)
        client.loop_start()

    while not wind_data:
        logging.info('Waiting for wind data... {}'.format(wind_speed))
        time.sleep(1)

    servo_pwm = PCA9685()
    servo_pwm.set_pwm_freq(60)

    gps_serial = serial.Serial(GPS_SERIAL_PORT, timeout=5.0)
    gps_thread = threading.Thread(target=gps_sensor, args=(gps_serial, gps_thread_stop))
    gps_thread.start()

    if COMPASS:
        bus = smbus.SMBus(1)
        compass_thread = threading.Thread(target=compass_sensor, args=(bus, compass_thread_stop))
        compass_thread.start()

        while True:
            sys, gyro, accel, mag = read_calibration_state(bus)
            logging.info('Calibration data: sys={}, gyro={}, accel={}, mag={}'.format(sys, gyro, accel, mag))

            if sys >= CALIBRATION_THRESHOLD and gyro >= CALIBRATION_THRESHOLD and accel >= 0 and mag >= CALIBRATION_THRESHOLD:
                logging.info('Calibration complete!')
                break
            time.sleep(0.2)
    else:
        bno_serial = BNO055.BNO055(serial_port=BNO_SERIAL_PORT, rst=18)
        while True:
            try:
                if not bno_serial.begin():
                    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
                break
            except RuntimeError:
                logging.warning('Got BNO Error, waiting one second...')
                time.sleep(1)

        while True:
            sys, gyro, accel, mag = bno_serial.get_calibration_status()
            logging.info('Calibration data: sys={}, gyro={}, accel={}, mag={}'.format(sys, gyro, accel, mag))
            time.sleep(0.1)
            if sys == 3 and gyro == 3 and accel == 3 and mag == 3:
                break

        bno_thread = threading.Thread(target=bno_sensor, args=(bno_serial, bno_thread_stop))
        bno_thread.start()

    with open('../json/waypoints.json') as f:
        waypoints = geojson.load(f)

    cyclic = waypoints['properties']['cyclic']
    logging.info('Waypoints: %s' % waypoints)
    logging.info('Number of coordinates: %d, Cyclic: %s' % (len(waypoints['geometry']['coordinates']), cyclic))

    while gps['status'] != 'A':
        logging.info('Waiting for gps...')
        time.sleep(0.2)

    while True:
        for i, waypoint in enumerate(waypoints['geometry']['coordinates']):
            logging.info('Using waypoint %i: %s' % (i, waypoint))
            geodesic = Geodesic.WGS84.Inverse(gps['lat'], gps['lon'], waypoint[1], waypoint[0])

            while geodesic['s12'] > TARGET_RADIUS:
                logging.info('Boat gps: {}, {}, timestamp={}, speed={}'.format(gps['lat'], gps['lon'], gps['timestamp'], gps['speed']))
                geodesic = Geodesic.WGS84.Inverse(gps['lat'], gps['lon'], waypoint[1], waypoint[0])

                logging.info('Distance to target: {:.2f}m'.format(geodesic['s12']))

                geodesic['azi1'] = (90 - geodesic['azi1']) % 360

                paths = calculate_initial_paths(geodesic['azi1'], geodesic['s12'])
                best_path = calculate_best_path(paths, PATH_CALCULATION_ITERATIONS)
                logging.debug('Best path is {}'.format(best_path))

                logging.info('Real boat heading is: {:.2f}'.format(boat_heading))

                heading_delta = (((best_path.get_heading() - boat_heading_x_y) + 180) % 360 - 180) * -1
                logging.info('Heading delta is: {:.2f}°'.format(heading_delta))

                rudder_servo_value = helpers.map_rudder_servo(heading_delta)

                logging.debug('Rudder servo value is: {:.2f}'.format(rudder_servo_value))
                servo_pwm.set_pwm(0, 0, rudder_servo_value)

                real_wind_vector = Vector(math.radians((wind_direction_x_y - 180) % 360), wind_speed)
                boat_vector = Vector(math.radians(boat_heading_x_y), gps['speed'])
                awv_boat = Vector.from_vector(np.subtract(real_wind_vector.get_vector(), boat_vector.get_vector()))

                delta = abs(boat_heading_x_y - (awv_boat.get_angle_degrees() + 180) % 360)

                if delta > 180:
                    delta = 360 - delta

                logging.info('Real wind speed: {:.2f} m/s / {:.2f} kn'.format(wind_speed, ms_to_kn(wind_speed)))
                logging.info('Real wind angle: {:.2f}°'.format(wind_direction))
                logging.info('Boat angle: {:.2f}°'.format(boat_heading))
                logging.info('Apparent wind angle: {:.2f}°'.format(delta))

                sail_angle = helpers.get_sail_angle(delta)

                logging.info('Sail angle is: {:.2f}°'.format(sail_angle))

                sail_servo_value = helpers.map_sail_servo(sail_angle)

                logging.debug('Sail servo value is: {:.2f}'.format(sail_servo_value))
                servo_pwm.set_pwm(1, 0, sail_servo_value)

                time.sleep(PATH_CALCULATION_TIMEOUT)
        if cyclic:
            logging.info('Start new cycle')
        else:
            logging.info('Finished course!')
            break
            # hold_position()
    shutdown_routine()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        gps_thread_stop.set()
        bno_thread_stop.set()
        compass_thread_stop.set()
    except Exception as e:
        logging.error('ERROR IN MAIN THREAD: {}'.format(e))
