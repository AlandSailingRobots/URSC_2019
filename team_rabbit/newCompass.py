#!/usr/bin/env python3
import smbus
import time
COMPASS_ADDRESS = 0x60

bus = smbus.SMBus(1)

def getBearing():
	bearing_LSB = bus.read_byte_data(0x60, 2)
	bearing_MSB = bus.read_byte_data(0x60, 3)
	bearing = (bearing_LSB << 8) + bearing_MSB
	bearing /= 10
	return bearing

if __name__ == "__main__":
	while 1:
		print("Bearing: ", getBearing())
		time.sleep(0.25)
