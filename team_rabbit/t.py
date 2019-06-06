import pigpio

def moveRudder(value):
	"""Moves the rudder along in range [-4,4], -4=left, 0=centre, 4=right"""
	gpio = pigpio.pi()
	gpio.set_mode(18, pigpio.OUTPUT)
	gpio.hardware_PWM(18, 50, 0)
	gpio.stop()

if __name__ == "__main__":
	while(1):
		moveRudder(1000000)
