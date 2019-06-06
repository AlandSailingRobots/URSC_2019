
import py_qmc5883l
import pigpio
gpio = pigpio.pi()
gpio.set_mode(18, pigpio.OUTPUT)
#sensor = py_qmc5883l.QMC5883L()

ZERO_ANGLE = 27650
MAX_ANGLE = 122520
ONE_DEG_STEP = 526

def angle_to_PWM(angle):
	result = abs(MAX_ANGLE - ONE_DEG_STEP* 1.5 * angle)
	if result < 40000:
		return 40000
	elif result > 115000:
		return 115000
	else:
		return result
while(1):
	#m = sensor.get_bearing()
	#print(m, end="\n")
	#gpio.hardware_PWM(18, 50, int(angle_to_PWM(m)))
	#print(angle_to_PWM(m), end="\n")
	gpio.hardware_PWM(18, 50, int(input("Input value: ")) )
