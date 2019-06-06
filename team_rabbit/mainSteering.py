import time
from math import sqrt
from math import ceil
from math import floor
from math import atan2
from math import pi
from newCompass import *
from mainGPS import *
from rudderMovement import *
from windCalculations import *
from geopy import distance
from datetime import datetime

def logGPS(x=None, y=None):
    if x == None:
        x,y=getGPS()
    f1= open("gpsData.txt", "a+")
    f1.write(str(datetime.now()) + "," + str(x) + "," + str(y) + "\n")
    f1.close()

def mainSteering(y, x, dx, dy): # Destination coords
    realAngle = (360 - getBearing()+ 90) % 360
    print("True Bearing", getBearing())
    print("Our coords: ", x, y)
    print("Dest coords: ", dx, dy)

    if((dx - x) != 0):
        print("Real angle: ", realAngle)
       #get the right dest angle, using tan-1()
        destinationAngle = atan2( (dy - y) , (dx - x) ) * 180 / pi
        print("Dest real angle: ", destinationAngle)
        difference = (realAngle - (destinationAngle % 360)) % 360
        print("Real difference: ", difference)
        if(difference < 180):
            print("Smaller than 180. Going, ", difference)
            moveRudder(ceil(-difference / 15))
        elif(difference >= 180):
            print("Bigger than 180. Going: ", 360-difference)
            moveRudder(floor((360 - difference) / 15))

if __name__ == "__main__":
    #if input("Predetermined? ") == "no":
       # dxs = [float(input("X: "))]
       # dys = [float(input("Y: ")) ] 
    if 1:
       dxs = [60.1046976, 60.1041240, 60.1044711,60.1048 ]
       dys = [19.9492564, 19.9491522, 19.950684, 19.946023]

    index = 0
    startTime = time.time()
    print("Mission start!")
    iteration = 0
    while(1):
        iteration += 1
        print("\n Iteration: ", iteration, "\n Mission time: ", round(time.time()-startTime))

        x, y = getGPS()
        logGPS(x,y)
        realDistance = distance.distance((x,y), (dxs[index],dys[index])).m

        analyzeWind(realDistance)
        mainSteering(x, y, float(dys[index]), float(dxs[index]))
        time.sleep(1)

        print("Distance to destination: ", round(realDistance,2))

        if realDistance < 5:
            index += 1
            index %= len(dxs)
            print("\n\nSuccess.")
            print("Next point.\n\n")
