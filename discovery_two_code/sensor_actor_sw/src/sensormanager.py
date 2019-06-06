# Script for managing Sensor Software Scripts for Sensors like
# BNO055 and GPS
import bno
import gps

bno.initBNO()
gps.writeHeaderIntoCSV();

while True:
    bno.readData();
    gps.writeGPSIntoCSV();