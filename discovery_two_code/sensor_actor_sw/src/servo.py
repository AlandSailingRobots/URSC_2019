# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
from datetime import datetime
import time
import curses
import os
#from pynput import keyboard
# Import the PCA9685 module.
import Adafruit_PCA9685
 
path = '' 
# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

def checkFileExists():
    global path
    path = os.getcwd() + "/logs/"
    if os.path.exists(path):
        if os.path.exists(path + "log_servo.txt"):
            print("Servo log already exists, Servo log will be deleted")
            os.remove(path + "log_servo.txt")
        else:
            print("No former Servo log found. Writing new data")
    else:
        print("Logs path not found. Creating...")
        os.mkdir(path,0755)

checkFileExists()

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(0, 0,"Hit 'q' to quit")
stdscr.refresh()

sail = {'min': 250, 'max': 500, 'speed': 2}
sail['middle'] = int(round((sail['max'] - sail['min']) / 2 + sail['min']))
rudder = {'min': 220, 'max': 450, 'speed': 2}
rudder['middle'] = int(round((rudder['max'] - rudder['min']) / 2 + rudder['min']))

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

key = ''
sail_value = sail['middle']
rudder_value = rudder['middle']

pwm.set_pwm(0, 0, rudder_value)
stdscr.addstr(1, 0, 'rudder: ' + str(sail_value))
pwm.set_pwm(1, 0, sail_value)
stdscr.addstr(2, 0, 'sail: ' + str(rudder_value))


with open(path + 'log_servo.txt', 'a') as f:
    
    try:
        while key != ord('q'):
            key = stdscr.getch()
            stdscr.addch(20, 25,key)
            stdscr.refresh()
            if key == curses.KEY_LEFT: 
                rudder_value -= rudder['speed']
                if rudder_value < rudder['min']:
                    rudder_value = rudder['min']
                pwm.set_pwm(0, 0, rudder_value)
                stdscr.addstr(1, 0, 'rudder: ' + str(rudder_value))
                f.write(str(datetime.now()) + ' rudder value: ' + str(rudder_value) + '\n')
                f.flush()
            elif key == curses.KEY_RIGHT: 
                rudder_value += rudder['speed']
                if rudder_value > rudder['max']:
                    rudder_value = rudder['max']
                pwm.set_pwm(0, 0, rudder_value)
                stdscr.addstr(1, 0, 'rudder: ' + str(rudder_value))
                f.write(str(datetime.now()) + ' rudder value: ' + str(rudder_value) + '\n')
                f.flush()
            elif key == curses.KEY_UP: 
                sail_value += sail['speed']
                if sail_value > sail['max']:
                    sail_value = sail['max']
                pwm.set_pwm(1, 0, sail_value)
                stdscr.addstr(2, 0, 'sail: ' + str(sail_value))
                f.write(str(datetime.now()) + ' sail value: ' + str(sail_value) + '\n')
                f.flush()
            elif key == curses.KEY_DOWN: 
                sail_value -= sail['speed']
                if sail_value < sail['min']:
                    sail_value = sail['min']
                pwm.set_pwm(1, 0, sail_value)
                stdscr.addstr(2, 0, 'sail: ' + str(sail_value))
                f.write(str(datetime.now()) + ' sail value: ' + str(sail_value) + '\n')
                f.flush()
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()
