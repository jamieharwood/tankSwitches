#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankSwitch
"""

from machine import Pin
from machine import RTC
import network
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation
from NeoPixelClass import NeoPixel

restHost = "http://192.168.86.240:5000"  # /{0}/"

functionSelectPin = Pin(5, Pin.IN, Pin.PULL_UP)  # D3
waterOnPin = Pin(4, Pin.IN, Pin.PULL_UP)  # D4
watchdog = Pin(4, Pin.IN, Pin.PULL_UP)  # D4

neoPin = 12
# np = neopixel.NeoPixel(Pin(12), 4)
np = NeoPixel(neoPin, 4)

powerLed = 0
pumpLed = 1
hoseLed = 2
irrigationLed = 3


# Set initial state
np.colour(powerLed, 'red')
np.colour(hoseLed, 'purple')
np.colour(irrigationLed, 'purple')
np.colour(pumpLed, 'purple')
np.write()


def getdeviceid():

    deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    deviceid = deviceid.replace('b\'', '')
    deviceid = deviceid.replace('\'', '')

    # print(deviceid)

    return deviceid


def getFullUrl(restFunction):
    # return restHost.replace('{0}', restFunction)

    return restHost + '/' + restFunction + '/'


def isstatechanged(state):
    returnvalue = 0
    # url = "http://192.168.86.240:5000/{0}/".replace('{0}', state)
    url = getFullUrl(state)

    print(url)

    try:
        response = urequests.get(url)

        returnvalue = int(response.text.replace('\"', ''))

        response.close()
    except:
        print('Fail www connect...')

    return returnvalue


def getissunrise():
    return isstatechanged('isSunrise')


def getissunset():
    return isstatechanged('isSunset')


def getip():
    sta_if = network.WLAN(network.STA_IF)
    temp = sta_if.ifconfig()

    return temp[0]


def testfornetwork():
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.active():
        print('Waiting for Wifi')

    while '0.0.0.0' == getip():
        print('Waiting for IP')


def main():
    testfornetwork()

    debug = False
    sensorname = 'switch-user'

    if debug:
        sensorname += '-debug'

    deviceid = getdeviceid()

    mySensorRegistation = SensorRegistation(deviceid)
    mySensorRegistation.register(sensorname, 'Hardware', 'JH')

    myheartbeat = HeartBeat(deviceid)
    myheartbeat.beat()

    mytime = TimeTank(deviceid)
    while not mytime.settime():
        pass
    # mytime.settime(1)

    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    isMinuteProcess = 0
    lastMin = 0
    gethour = 0

    vars.functionSelect = functionSelectPin.value()
    vars.waterOn = waterOnPin.value()

    if vars.functionSelect:
        np.colour(irrigationLed, 'indigo')
        np.colour(hoseLed, 'purple')
    else:
        np.colour(irrigationLed, 'purple')
        np.colour(hoseLed, 'indigo')

    if vars.waterOn:
        np.colour(pumpLed, 'purple')
    else:
        np.colour(pumpLed, 'green')

    np.write()

    while True:
        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currMinute not in sampletimes and isMinuteProcess == 0:
            # process goes here

            isMinuteProcess = 1

        if currMinute in sampletimes and isMinuteProcess == 1:
            # process goes here

            isMinuteProcess = 0

        if lastMin != currMinute:
            # process goes here
            myheartbeat.beat()

            lastMin = currMinute

        if currHour not in samplehours and gethour == 0:
            gethour = 1

        if currHour in samplehours and gethour == 1:
            gethour = 0
            local = utime.localtime()
            while not mytime.settime():
                pass
            # mytime.settime(1)

        # Read switch inputs
        vars.functionSelect = functionSelectPin.value()
        vars.waterOn = waterOnPin.value()
        functionStateChanged = False
        sensorValue = 0

        # Check against the last input
        if vars.functionSelect != vars.functionSelectLast:
            if vars.functionSelect:
                np.colour(irrigationLed, 'indigo')
                np.colour(hoseLed, 'purple')
            else:
                np.colour(irrigationLed, 'purple')
                np.colour(hoseLed, 'indigo')

            functionStateChanged = True

            vars.functionSelectLast = vars.functionSelect  # Set the last pointers
            # print('if ( functionSelect != functionSelectLast ):')

        if vars.waterOn != vars.waterOnLast:
            if vars.waterOn:  # water on
                np.colour(pumpLed, 'purple')
            else:  # water off
                np.colour(pumpLed, 'green')

            functionStateChanged = True

            vars.waterOnLast = vars.waterOn  # Set the last pointers
            # print('if ( waterOn != waterOnLast ):')

        if functionStateChanged:

            if vars.functionSelect:
                sensorValue = 1
            else:
                sensorValue = 2

            if not vars.waterOn:  # water on
                sensorValue += 4

            url = "http://192.168.86.240:5000/sensorStateWrite/{0}/{1}/{2}"
            url = url.replace('{0}', deviceid)  # sensor id
            url = url.replace('{1}', sensorname)  # sensor type
            url = url.replace('{2}', str(sensorValue))  # sensor value

            print(url)

            try:
                response = urequests.get(url)

                print(response.text)

                response.close()
            except:
                print('Fail www connect...')

        np.write()


main()
