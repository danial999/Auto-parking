#!/usr/bin/env python
import serial
import time


"""
class LegoCarSerial(object) - we have created a class which is responsible for communicating with an arduino device as follows:
Requirements:
	- port - holds the actual PC port from which the data will be send to the arduino device.
	- buad_rate - holds the baud rate of the communication between the PC and the arduino device.
	- arduinoSerial - holds the opened serial which is responsible for sending our data to the arduino.
"""
class LegoCarSerial(object):
    port = ""
    baud_rate = 0
    arduinoSerial = ""
    def  __init__(self,port,baud_rate):
        self.__class__.port = port
        self.__class__.baud_rate = baud_rate
        self.__class__.arduinoSerial = ""

    def openSerial(self):
        self.__class__.arduinoSerial = serial.Serial(self.port,self.baud_rate)

    def sendData(self,commands):
        commands = list(commands)

        #print(commands)
        if(len(commands) == 1):
            self.__class__.arduinoSerial.write(commands[0])

        elif(len(commands) == 2):
            self.__class__.arduinoSerial.write(commands[0])
            time.sleep(0.05)
            self.__class__.arduinoSerial.write(commands[1])


    def closeSerial(self):
        self.__class__.arduinoSerial.close()
        self.__class__.arduinoSerial = ""


    def __del__(self):
        class_name = self.__class__.__name__
        print(class_name + " destroyed")

