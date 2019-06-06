import time
import json
import serial
import csv
import os
from datetime import datetime
from geojson import Feature, Point

header = ['timestamp', 'latitude', 'longitude']
path = ''
ser = serial.Serial(
   port='/dev/ttyACM0',
   baudrate = 9600,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS,
   timeout=1
)

def checkFileExists():
    global path
    path = os.getcwd() + "/logs/"
    if os.path.exists(path):
        if os.path.exists(path + "gps.csv"):
            print("GPS log already exists, GPS log will be deleted")
            os.remove(path + "gps.csv")
        else:
            print("No former GPS log found. Writing new data")
    else:
        print("Logs path not found. Creating...")
        os.mkdir(path,0755)
    
def writeHeaderIntoCSV():
    checkFileExists()
    with open(path + 'gps.csv', 'a') as f:
        csv_writer = csv.writer(f)
     
        csv_writer.writerow(header) # write header
    
def writeGPSIntoCSV():
    with open(path + 'gps.csv', 'a') as f:
        csv_writer = csv.writer(f)
        arr = ser.readline().strip().decode('ascii').split(',')
        if arr[0] == '$GNGLL' and arr[1] != '':
            row = [datetime.now().isoformat(), float(arr[1])/100,float(arr[3])/100]
            #print(row)
            csv_writer.writerow(row)
        
def readGPSIntoTextfile():
    with open(path + 'log_gps.txt', 'a') as f:
       arr = ser.readline().strip().decode('ascii').split(',')
       print(arr)
       if arr[0] == '$GNGLL' and arr[1] != '':
           point = Point((float(arr[1]), float(arr[3])))
           feature = Feature(geometry=point, properties={'timestamp': datetime.now().isoformat()})
           print(feature)
           f.write(json.dumps(feature) + '\n')
           f.flush()
