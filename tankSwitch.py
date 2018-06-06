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
# import varibles as vars
import urequests
import ubinascii
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation
from NeoPixelClass import NeoPixel

restHost = 'http://192.168.86.240:5000'

__functionSelectPin = Pin(5, Pin.IN, Pin.PULL_UP)  # D3
__waterOnPin = Pin(4, Pin.IN, Pin.PULL_UP)  # D4
# __watchdog = Pin(4, Pin.IN, Pin.PULL_UP)  # D4

__neoPin = 12
__np = NeoPixel(__neoPin, 4)

powerLed = 0
pumpLed = 1
hoseLed = 2
irrigationLed = 3


# Set initial state
__np.colour(powerLed, 'red')
__np.colour(hoseLed, 'purple')
__np.colour(irrigationLed, 'purple')
__np.colour(pumpLed, 'purple')
__np.write()

__sensorname = ''
__deviceid = ''

__functionSelect = 0
__functionSelectLast = -1
__waterOn = 0
__waterOnLast = -1


def getdeviceid():
    global __deviceid

    __deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    __deviceid = __deviceid.replace('b\'', '')
    __deviceid = __deviceid.replace('\'', '')

    return __deviceid


def getFullUrl(restFunction):

    return restHost + '/' + restFunction + '/'


def isstatechanged(state):
    returnvalue = 0

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
    global __sensorname, __deviceid, __functionSelect, __waterOn, __functionSelectLast
    testfornetwork()
    
    debug = False
    __sensorname = 'switch-user'
    __deviceid = getdeviceid()

    if debug:
        __sensorname += "-" + __deviceid + '-debug'

    mySensorRegistation = SensorRegistation(restHost, __deviceid)
    mySensorRegistation.register(__sensorname, 'Hardware', 'JH')

    myheartbeat = HeartBeat(restHost, __deviceid)
    myheartbeat.beat()

    mytime = TimeTank(__deviceid)
    while not mytime.settime():
        pass

    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    isMinuteProcess = 0
    lastMin = 0
    gethour = 0

    __functionSelect = __functionSelectPin.value()
    __waterOn = __waterOnPin.value()

    if __functionSelect:
        __np.colour(irrigationLed, 'indigo')
        __np.colour(hoseLed, 'purple')
    else:
        __np.colour(irrigationLed, 'purple')
        __np.colour(hoseLed, 'indigo')

    if __waterOn:
        __np.colour(pumpLed, 'purple')
    else:
        __np.colour(pumpLed, 'green')

    __np.write()

    while True:
        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currMinute not in sampletimes and isMinuteProcess == 0:
            isMinuteProcess = 1

        if currMinute in sampletimes and isMinuteProcess == 1:
            isMinuteProcess = 0

        if lastMin != currMinute:
            lastMin = currMinute

            myheartbeat.beat()

        if currHour not in samplehours and gethour == 0:
            gethour = 1

        if currHour in samplehours and gethour == 1:
            gethour = 0

            local = utime.localtime()
            while not mytime.settime():
                pass

        # Read switch inputs
        __functionSelect = __functionSelectPin.value()
        __waterOn = __waterOnPin.value()
        functionStateChanged = False
        sensorValue = 0

        # Check against the last input
        if __functionSelect != __functionSelectLast:
            if __functionSelect:
                __np.colour(irrigationLed, 'indigo')
                __np.colour(hoseLed, 'purple')
            else:
                __np.colour(irrigationLed, 'purple')
                __np.colour(hoseLed, 'indigo')

            functionStateChanged = True

            __functionSelectLast = __functionSelect  # Set the last pointers
            # print('if ( __functionSelect != __functionSelectLast ):')

        if __waterOn != __waterOnLast:
            if __waterOn:  # water on
                __np.colour(pumpLed, 'purple')
            else:  # water off
                __np.colour(pumpLed, 'green')

            functionStateChanged = True

            __waterOnLast = __waterOn  # Set the last pointers
            # print('if ( __waterOn != __waterOnLast ):')

        if functionStateChanged:

            if __functionSelect:
                sensorValue = 1
            else:
                sensorValue = 2

            if not __waterOn:  # water on
                sensorValue += 4

            url = "http://192.168.86.240:5000/sensorStateWrite/{0}/{1}/{2}"
            url = url.replace('{0}', __deviceid)  # sensor id
            url = url.replace('{1}', __sensorname)  # sensor type
            url = url.replace('{2}', str(sensorValue))  # sensor value

            print(url)

            try:
                response = urequests.get(url)

                print(response.text)

                response.close()
            except:
                print('Fail www connect...')

        __np.write()


main()

