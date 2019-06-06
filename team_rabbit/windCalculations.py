from moveSail import *
from rudderMovement import *
from newCompass import *
from mainGPS import *
import random
import time
from geopy import distance
from mainSteering import logGPS
#get wind from mqtt
def tacking(windDegree, distanceToDest):
	if 'lastTack' not in tacking.__dict__:
		tacking.lastTack = -1
	else:
		tacking.lastTack *= -1
	#move rudder in the direction of lastTack

	moveRudder(6 * tacking.lastTack)
	print("\nTacking started\nMoving rudder to 40d. ", tacking.lastTack)
	print("Wind direction: ", windDegree)
	angleCalc = 0
	while angleCalc < 35:
		angleCalc = (getBearing() - windDegree+180) % 360
		if angleCalc > 180:
			angleCalc = 360 - angleCalc
		print("Waiting for orientation to align 40d. ")
		print("Bearing: ", getBearing())
		print("Relative wind angle: ", angleCalc)
		time.sleep(0.5)
	moveRudder(0) #go in a straight line
	moveSail(5) #30d sail position

	startingPoint = getGPS()
	print("Moving at a 40d angle for: ", round(distanceToDest/2), "m")
	movedFor = 0
	iteration = 0;markerMove = 0
	while movedFor < distanceToDest/5:
		movedFor = distance.distance(startingPoint, getGPS()).m
		time.sleep(2) #check every 5s if we've moved an amount of m
		iteration+=1
		if iteration > 10: #if by 20s we don't at least 5m, change angle
			if abs(markerMove - movedFor) < 5 or markerMove > movedFor:
				print("\nDrifting too much, chaning angles.")
				moveRudder(tacking.lastTack * 8)
				time.sleep(5)
				break
			markerMove = movedFor
			iteration = 0
		print("Distance left: ", distanceToDest/2 - movedFor, "m")
		print("Current GPS: ", getGPS())
		logGPS()
	print("Tacking Stopped")

def analyzeWind(distanceToDest):
	windDegree = 340
	print("Current wind: ", windDegree)

	compassBearing = getBearing()

	difference = (windDegree - compassBearing) % 360

	if difference > 180:
		difference = (360-difference)

	print("Wind to Bear diff: ", difference)

	if difference > 150: #180 +- 30
		#we are in irons
		print("In irons")
		moveSail(4)
		tacking(windDegree, distanceToDest)
	elif difference > 120: #irons +- 30
		print("From the side, 1")
		moveSail(5)
	elif difference > 90:
		print("From the side, 2")
		moveSail(7)
	elif difference  > 60:
		print("From the side, 3")
		moveSail(8)
	elif difference > 30:
		print("From the side, 4")
		moveSail(9)
	else:
		print("From behind")
		moveSail(10)

if __name__ == "__main__":
	while True:
		analyzeWind(2)
		input()

