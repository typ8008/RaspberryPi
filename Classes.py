#!/usr/bin/python
import smbus

class TMP102():
    'Class for Temperature Sensor I2C TMP102'

    def __init__(self,smAddress, moduleAddress):
        self.smAddress = smAddress
        self.moduleAddress = moduleAddress
        
    def getTemperature(self):
        bus = smbus.SMBus(self.smAddress) # Create bus object
        raw = bus.read_word_data(self.moduleAddress,0) # read word data from sensor    
        msb = raw & 0xFF # MSB from raw data
        lsb = raw >> 8 # LSB from raw data
        raw = (msb * 256 + lsb) >> 4 # remove insignificant bits
     
        neg = raw & 0x0800 # check if temperature is negative
        if (neg > 0):
            print ('negative')
            comp2 = (~raw & 0x0FFF) + 1
            raw = comp2 * -1
     
        reading = raw * 0.0625 # Shift 5 Left to remove unused bytes and multiply by resolution
        del bus # remove bus object
        return reading