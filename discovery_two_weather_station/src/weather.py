#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import json
import curses
import random
import locale
import argparse
import threading
import collections
import RPi.GPIO as GPIO
import paho.mqtt.publish as publish

from time import sleep
from asciichartpy import plot
from gpiozero import MCP3008
from datetime import datetime

__author__ = "Fabian Wurster"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "fwurster@stud.hs-heilbronn.de"

SPEED_KMH = 2.5
SPEED_MS = SPEED_KMH / 3.6

DIRECTIONS = {3.84: 0, 1.98: 22.5, 2.25: 45, 0.41: 67.5, 0.45: 90, 0.32: 112.5, 0.9: 135, 0.62: 157.5, 1.4: 180, 1.19: 202.5, 3.08: 225, 2.93: 247.5, 4.62: 270, 4.04: 292.5, 4.33: 315, 3.43: 337.5}

locale.setlocale(locale.LC_ALL, 'C.UTF-8')

class WeatherStation:
    lastValidDirection = 0
    speed = 0.0
    speed_counter = 0
    speed_lock = threading.Lock()
    tmp = MCP3008(channel=0, device=0)

    def __init__(self, mqtt_server, mqtt_path, speed_pin, direction_error, direction_error_send, direction_precision, send_sleep):
        self.mqtt_server = mqtt_server
        self.mqtt_path = mqtt_path
        self.speed_pin = speed_pin
        self.direction_error = direction_error
        self.direction_error_send = direction_error_send
        self.direction_precision = direction_precision
        self.send_sleep = send_sleep

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.speed_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.speed_pin, GPIO.RISING, callback=self.speed_switch)

        t1 = threading.Thread(target=self.speed_timer)
        t1.start()

    def speed_switch(self, channel):
        with self.speed_lock:
            self.speed_counter += 1

    def speed_timer(self):
        while True:
            with self.speed_lock:
                self.speed = round(SPEED_MS * self.speed_counter, 2)
                self.speed_counter = 0
            sleep(1)

    def gui(self, scr):
        scr.clear()
        rows, columns = os.popen('stty size', 'r').read().split()
        rows = int(rows)
        columns = int(columns)

        plot_width = int(columns * 0.8)
        deque_dir = collections.deque([0] * plot_width, maxlen=plot_width)
        deque_speed = collections.deque([0] * plot_width, maxlen=plot_width)

        while(True):
            value = self.tmp.value * 5.0
            direction = self.map_direction(value)
            deque_dir.popleft()
            deque_speed.popleft()
            deque_dir.append(direction)
            deque_speed.append(self.speed)
            scr.addstr(0,0, 'DIRECTION')
            scr.addstr(2, 0, plot(deque_dir, {'minimum': 0.0, 'maximum': 360.0, 'height': 16 }))
            scr.addstr(20, 0, 'SPEED')
            scr.addstr(22, 0, plot(deque_speed, {'minimum': 0.0, 'maximum': 20, 'height': 20 }))
            scr.refresh()
            publish.single(self.mqtt_path, self.build_json_package(direction, self.speed), hostname=self.mqtt_server)
            sleep(self.send_sleep)

    def headless(self):
        while(True):
            value = self.tmp.value * 5.0
            direction = self.map_direction(value)
            publish.single(self.mqtt_path, self.build_json_package(direction, self.speed), hostname=self.mqtt_server)
            sleep(self.send_sleep)

    def map_direction(self, direction_voltage):
        for voltage in DIRECTIONS:
            if abs(voltage - direction_voltage) < self.direction_precision:
                direction = DIRECTIONS.get(voltage)
                self.lastValidDirection = direction
                return direction
        if self.direction_error_send:
            return self.direction_error
        else:
            return self.lastValidDirection

    def build_json_package(self, direction, speed):
        return json.dumps({'speed': speed, 'direction': direction, 'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--server', '-s', default='localhost', dest='mqtt_server', help='the ip of the mqtt server')
    parser.add_argument('--path', '-p', default='weather', dest='mqtt_path', help='the path of mqtt packets')
    parser.add_argument('--speed', default=25, dest='speed_pin', help='the gpio pin which is connected to the wind speed sensor')
    parser.add_argument('--dir-error', default=359, dest='direction_error', help='the direction value that will be written if an invalid direction was read')
    parser.add_argument('--dir-prec', default=0.015, dest='direction_precision', help='the precision in Volts of the mapped direction values')
    parser.add_argument('--dir-error-send', action='store_true', dest='direction_error_send', help='enable to send the error value, if disabled the weather station will send the last valid value')
    parser.add_argument('--send-sleep', default=0.2, dest='send_sleep', help='the time in seconds between two mqtt packets')
    parser.add_argument('--chart', '-c', action='store_true', dest='chart', help='enable asciichartpy')
    args = parser.parse_args()
    try:
        w = WeatherStation(args.mqtt_server, args.mqtt_path, args.speed_pin, args.direction_error, args.direction_error_send, args.direction_precision, args.send_sleep)
        if args.chart:
            curses.wrapper(w.gui)
        else:
            w.headless()
    except KeyboardInterrupt:
        try:
            GPIO.cleanup()
            sys.exit(0)
        except SystemExit:
            os._exit(0)
