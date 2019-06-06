import unittest
import os, sys

current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
sys.path.append(parent_path)

from sailboatcontrol import helpers

SAIL_ANGLE_TESTS = {
    'sail': {
        '0': 0,
        '45': 22.5,
        '90': 45,
        '135': 67.5,
        '180': 90,
        '225': 67.5,
        '270': 45,
        '315': 22.5,
        '360': 0
    }
}

RUDDER_SERVO_TESTS = {
    'rudder': {
        '0': 335,
        '45': 392,
        '90': 450,
        '180': 450,
        '181': 220,
        '270': 220,
        '315': 278,
        '360': 335
    }
}

SAIL_SERVO_TESTS = {
    'sail': {
        '0': 500,
        '22.5': 438,
        '45': 375,
        '67.5': 312,
        '90': 250,
    }
}


class BasicTestSuite(unittest.TestCase):
    def test_get_sail_angle(self):
        for angle in SAIL_ANGLE_TESTS['sail']:
            self.assertEqual(SAIL_ANGLE_TESTS['sail'][angle], helpers.get_sail_angle(float(angle)))

    def test_map_rudder_servo(self):
        for angle in RUDDER_SERVO_TESTS['rudder']:
            self.assertEqual(RUDDER_SERVO_TESTS['rudder'][angle], helpers.map_rudder_servo(float(angle)))

    def test_map_sail_servo(self):
        for angle in SAIL_SERVO_TESTS['sail']:
            self.assertEqual(SAIL_SERVO_TESTS['sail'][angle], helpers.map_sail_servo(float(angle)))


if __name__ == '__main__':
    unittest.main()
