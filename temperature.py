#!/usr/bin/python

import time
import Classes

i2C_address = 1
device_address = 0x48

temp1 = Classes.TMP102(i2C_address,device_address)

while True:
    temperature = temp1.getTemperature()
    print ('temperature: {0:0.2f} *C'.format(temperature)) # Display as floating point with 2 decimal point accuracy
    time.sleep(5)