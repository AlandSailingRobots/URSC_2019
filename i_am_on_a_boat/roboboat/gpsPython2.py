import os
import time
import pynmea2
import serial
import string

def getCoord():
	try:
		if 'lat' not in getCoord.__dict__:
			getCoord.lat = 0
		if 'lon' not in getCoord.__dict__:
			getCoord.lon = 0		# Some half-assed static variables
		ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=10) # Open serial comm on ttyS0
		dataout = pynmea2.NMEAStreamReader()	# This is our GPS code parser
		timing = 0
		while 1:
			newdata = ser.readline()		# Read a line from serial device
			if newdata[0:6] == '$GPGGA':		# If line contains GPS coordinate info
				newmsg = pynmea2.parse(newdata)	# Parse it
				getCoord.lat = newmsg.latitude	# Store the values accordingly
				getCoord.lon = newmsg.longitude
				break
		ser.close()				# Close serial comm
	except KeyboardInterrupt:
		ser.close()
		quit()

	return getCoord.lat, getCoord.lon

timing = 0
while timing < 5:
	lat,long = getCoord()
	if lat != 0 or long !=0:
		break
	timing += 1
	#print lat,long
	#print "Waiting for lock"
print lat,long
