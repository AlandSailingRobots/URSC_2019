#!/usr/bin/env python

import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt

WIND_SPEED_MS = 15
WIND_DIRECTION_DEGREE = 0


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def build_json_package(direction, speed):
    return json.dumps({'speed': speed, 'direction': direction,
                       'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})


def knots_to_ms(knots):
    return knots / 1.944


def main():
    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("localhost", 1883, 60)

    client.loop_start()

    while True:
        time.sleep(1)
        client.publish("weather", build_json_package(WIND_DIRECTION_DEGREE, knots_to_ms(WIND_SPEED_MS)))


if __name__ == '__main__':
    main()
