import time
from math import *
import smbus

from returnCompass import returnAngle
from i2c_rudder import *
from sys import argv
import gps
import requests


import os
from gps import *
from time import *
import time
import threading


 
gpsd = None #seting the global variable
 
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer


def mainSteering(x, y):
    x = 0
    y = 0

    heading_angle = returnAngle() #Angle from Compass
    bearing = (360 - heading_angle+ 90) % 360
    print("Heading Angle: ", heading_angle)
    print("Bearing to destination: ", bearing)

    # Get GPS - from the GPS, the values..
    # x, y = getGPS()
    # x = gpsd.fix.latitude  #Static values for x and y given from the returnGPS function 60.105200, 19.945613
    # y = gpsd.fix.longitude
    print("gpsd x" ,x)
    print("gpsd y", y)
    
    # print("Current Coordinates: ", returnAngle.rep.lat)
    # print("Current Coordinates: ", gpsPython2.getCoord.lat, gpsPython2.getCoord.lon)
    # print("GPS Current Coordinates: ", x, y)
    # dx = [60.105185, 60.104767, 60.104877]
    # dy = [19.946151, 19.945548, 19.946616]
    dx = 62.105085
    dy = 19.945476
    print("Destination Coordinates: ", dx, dy)

    # Get the Coordinates differences and Destination Angle -- --
    differenceX = dx - x
    differenceY = dy - y
    destinationAngle = atan2( (differenceX) , (differenceY) ) * 180 / pi
    print("Destination Angle: ", destinationAngle)
    difference = (bearing - destinationAngle) % 360
    print("Difference: ", difference)

    # Rudder  -- --
    if(difference < 180):
        print("Smaller than 180. Going, ", difference)
        # rudder_contoller(int(60))
        rudder_contoller(ceil(difference / 1.5))
        
    elif(difference >= 180):
        print("Bigger than 180. Going: ", 360 - difference)
        rudder_contoller(floor((360 - difference) / 1.5))
    time.sleep(0.25)

        

# if __name__ == '__main__':
#     gpsp = GpsPoller() # create the thread
#     try:
#         while True:
            
#             gpsp.start() # start it up

#             #It may take a second or two to get good data
#             #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc

#             print('latitude: ' , gpsd.fix.latitude)
#             x = gpsd.fix.latitude
#             print('longitude: ' , gpsd.fix.longitude)
#             y= gpsd.fix.longitude

#         mainSteering(x, y)


