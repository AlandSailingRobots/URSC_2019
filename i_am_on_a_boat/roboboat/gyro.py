#!/usr/bin/python
import smbus
import math
import time
 

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def read_byte(reg):
    return bus.read_byte_data(address, reg)
 
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
 
def dist(a,b):
    return math.sqrt((a*a)+(b*b))
 
def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)
 
def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
 
bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68       # via i2cdetect
 
# Aktivieren, um das Modul ansprechen zu koennen
bus.write_byte_data(address, power_mgmt_1, 0)
 


print ("Gyroscope")
print ("--------")
try:
  while True:
    
    
    gyroscope_xout = read_word_2c(0x43)
    gyroscope_yout = read_word_2c(0x45)
    gyroscope_zout = read_word_2c(0x47)
    
    print ("gyro_xout: ", ("%5d" % gyroscope_xout), "  scaled: ", (gyroscope_xout / 131))
    print ("gyro_yout: ", ("%5d" % gyroscope_yout), "  scaled: ", (gyroscope_yout / 131))
    print ("gyro_zout: ", ("%5d" % gyroscope_zout), "  scaled: ", (gyroscope_zout / 131))
    
    print("")
    print ("Sensor result")
    print ("---------------------")


    beschleunigung_xout = read_word_2c(0x3b)
    beschleunigung_yout = read_word_2c(0x3d)
    beschleunigung_zout = read_word_2c(0x3f)
    
    beschleunigung_xout_skaliert = beschleunigung_xout / 16384.0
    beschleunigung_yout_skaliert = beschleunigung_yout / 16384.0
    beschleunigung_zout_skaliert = beschleunigung_zout / 16384.0
    
    print ("x_out: ", ("%6d" % beschleunigung_xout), "  scaled: ", beschleunigung_xout_skaliert)
    print ("y_out: ", ("%6d" % beschleunigung_yout), "  scaled: ", beschleunigung_yout_skaliert)
    print ("z_out: ", ("%6d" % beschleunigung_zout), "  scaled: ", beschleunigung_zout_skaliert)
    
    print ("X Rotation: " , get_x_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert))
    print ("Y Rotation: " , get_y_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert))

    time.sleep(1)

except KeyboardInterrupt:
    exit()
  