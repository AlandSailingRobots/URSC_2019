import time
from adafruit_servokit import ServoKit
 
# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

userInput = 0

def rudder_contoller(userInput):
        # userInput = float(60)
        kit.servo[4].angle = userInput

# rudder_contoller(userInput)