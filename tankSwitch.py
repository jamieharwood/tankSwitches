#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankSwitch
"""

from machine import Pin
from machine import RTC
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

host = "0.uk.pool.ntp.org"

restHost = "http://192.168.86.240:5000/{0}/"

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


def time():
    try:
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
        addr = socket.getaddrinfo(host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
        s.close()
        val = struct.unpack("!I", msg[40:44])[0]

        return val - NTP_DELTA
    except OSError:

        return 0

# There's currently no timezone support in MicroPython, so
# utime.localtime() will return UTC time (as if it was .gmtime())


def settime():
    while time() == 0:
        print('Waiting for time...')

    t = time()
    import machine
    import utime
    tm = utime.localtime(t)
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    machine.RTC().datetime(tm)
    print(utime.localtime())


def getdeviceid():

    deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    deviceid = deviceid.replace('b\'', '')
    deviceid = deviceid.replace('\'', '')

    print(deviceid)

    return deviceid


def getFullUrl(restFunction):

    return restHost.replace('{0}', restFunction)


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
        #  remoteHose = False
        #  remoteIrrigation = False
        #  remotePump = False
        print('Fail www connect...')

    return returnvalue


def heartbeat(sendorid):
    #returnvalue = 0
    url = "http://192.168.86.240:5000/sensorHeartbeat/{0}".replace('{0}', sendorid)
    #url = getFullUrl(state)

    print(url)

    try:
        response = urequests.get(url)

        #returnvalue = int(response.text.replace('\"', ''))

        response.close()
    except:
        #  remoteHose = False
        #  remoteIrrigation = False
        #  remotePump = False
        print('Fail www connect...')

    #return returnvalue


def getissunrise():
    return isstatechanged('isSunrise')


def getissunset():
    return isstatechanged('isSunset')


def main():

    settime()
    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    isMinuteProcess = 0
    lastMin = 0
    gethour = 0

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
    heartbeat(deviceid)

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
            heartbeat(deviceid)

            lastMin = currMinute

        if currMinute not in samplehours and gethour == 0:
            gethour = 1

        if currMinute in samplehours and gethour == 1:
            gethour = 0
            local = utime.localtime()
            settime()

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
            url = url.replace('{1}', 'switch-user')  # sensor type
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
