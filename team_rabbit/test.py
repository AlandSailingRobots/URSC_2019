#!/usr/bin/env python3
import py_qmc5883l

def readCompass():
	"""Returns compass bearing."""
	sensor = py_qmc5883l.QMC5883L()
	return sensor.get_bearing() - 90

def realAngle(angle):
        return (360 - angle) % 360

if __name__ == "__main__":
	while(1):
                bearing = readCompass()
                print("Bearing: ", bearing)
