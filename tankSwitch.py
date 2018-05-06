#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankSwitch
"""

from machine import Pin
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

functionSelectPin = Pin(5, Pin.IN, Pin.PULL_UP)  # D3
waterOnPin = Pin(4, Pin.IN, Pin.PULL_UP)  # D4

np = neopixel.NeoPixel(Pin(12), 4)
neoLow = 0
neoMid = 64
neoHi = 255

red = (neoMid, neoLow, neoLow)
yellow = (255, 226, neoLow)
tango = (243, 114, 82)
green = (neoLow, neoMid, neoLow)
indigo = (neoLow, 126, 135)
blue = (neoLow, neoLow, neoMid)
purple = (neoMid, neoLow, neoMid)
black = (neoLow, neoLow, neoLow)

powerLed = 0
pumpLed = 1
hoseLed = 2
irrigationLed = 3


# Set initial state
np[powerLed] = red
np[hoseLed] = purple
np[irrigationLed] = purple
np[pumpLed] = purple
np.write()


def getdeviceid():

    deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    deviceid = deviceid.replace('b\'', '')
    deviceid = deviceid.replace('\'', '')

    print(deviceid)

    return deviceid


def main():

    vars.functionSelect = functionSelectPin.value()
    vars.waterOn = waterOnPin.value()

    if vars.functionSelect:
        np[irrigationLed] = indigo
        np[hoseLed] = purple
    else:
        np[irrigationLed] = purple
        np[hoseLed] = indigo

    if vars.waterOn:
        np[pumpLed] = purple
    else:
        np[pumpLed] = green

    np.write()

    deviceid = getdeviceid()

    while True:
        # Read switch inputs
        vars.functionSelect = functionSelectPin.value()
        vars.waterOn = waterOnPin.value()
        functionStateChanged = False
        sensorValue = 0

        # Check against the last input
        if vars.functionSelect != vars.functionSelectLast:
            if vars.functionSelect:
                np[irrigationLed] = indigo
                np[hoseLed] = purple
            else:
                np[irrigationLed] = purple
                np[hoseLed] = indigo

            functionStateChanged = True

            vars.functionSelectLast = vars.functionSelect  # Set the last pointers
            print('if ( functionSelect != functionSelectLast ):')

        if vars.waterOn != vars.waterOnLast:
            if vars.waterOn:  # water on
                np[pumpLed] = purple
            else:  # water off
                np[pumpLed] = green

                #if vars.functionSelect:
                    #np[irrigationLed] = green
                #else:
                    #np[hoseLed] = green

            functionStateChanged = True

            vars.waterOnLast = vars.waterOn  # Set the last pointers
            print('if ( waterOn != waterOnLast ):')

        if functionStateChanged:

            if vars.functionSelect:
                sensorValue = 1
            else:
                sensorValue = 2

            if vars.waterOn != True:  # water on
                sensorValue += 4

            url = "http://192.168.86.240:5000/sensorStateWrite/{0}/{1}/{2}"
            url = url.replace('{0}', deviceid)  # sensor id
            url = url.replace('{1}', 'dim_led')  # sensor type
            url = url.replace('{2}', str(sensorValue))  # sensor value

            print(url)

            try:
                response = urequests.get(url)

                print(response.text)

                response.close()
            except:
                print('Fail www connect...')
            # Save some cycles

        np.write()


main()
