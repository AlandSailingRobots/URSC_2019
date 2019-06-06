import pigpio

def moveRudder(value):
	"""Moves the rudder along in range [-4,4], -4=left, 0=centre, 4=right"""
	gpio = pigpio.pi()
	gpio.set_mode(19, pigpio.OUTPUT)
	gpio.hardware_PWM(19, 50, 77500 + value *2400)
	gpio.stop()

if __name__ == "__main__":
	while(1):
		moveRudder(int(input("Enter -11 to 11: ")))
