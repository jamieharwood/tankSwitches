from machine import Pin
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

functionSelectPin = Pin(5, Pin.IN, Pin.PULL_UP)  # D3
waterOnPin = Pin(4, Pin.IN, Pin.PULL_UP)  # D4
neoMid = 64
neoHi = 255

functionStateChanged = False


def main():
    np = neopixel.NeoPixel(machine.Pin(12), 4)

    # Set initial state
    np[0] = (255, 0, 0)
    np[1] = (neoMid, 0, neoMid)
    np[2] = (neoMid, 0, neoMid)
    np[3] = (neoMid, 0, neoMid)
    np.write()

    vars.functionSelect = functionSelectPin.value()
    vars.waterOn = waterOnPin.value()

    if vars.functionSelect:
        np[1] = (neoMid, 0, neoMid)
        np[2] = (0, neoHi, 0)
    else:
        np[1] = (0, neoHi, 0)
        np[2] = (neoMid, 0, neoMid)

    if vars.waterOn:
        np[3] = (neoMid, 0, neoMid)
    else:
        np[3] = (0, neoHi, 0)

    np.write()

    while True:
        # Read switch inputs
        vars.functionSelect = functionSelectPin.value()
        vars.waterOn = waterOnPin.value()
        functionStateChanged = False
        sensorValue = 0

        # Check against the last input
        if vars.functionSelect != vars.functionSelectLast:
            if vars.functionSelect:
                np[1] = (neoMid, 0, neoMid)
                np[2] = (0, neoHi, 0)
            else:
                np[1] = (0, neoHi, 0)
                np[2] = (neoMid, 0, neoMid)

            functionStateChanged = True

            vars.functionSelectLast = vars.functionSelect  # Set the last pointers
            print('if ( functionSelect != functionSelectLast ):')

        if vars.waterOn != vars.waterOnLast:
            if vars.waterOn:  # water on
                np[3] = (neoMid, 0, neoMid)
            else:  # water off
                np[3] = (0, neoHi, 0)

            functionStateChanged = True

            vars.waterOnLast = vars.waterOn  # Set the last pointers
            print('if ( waterOn != waterOnLast ):')

        if functionStateChanged:

            deviceid = ubinascii.hexlify(machine.unique_id()).decode()
            deviceid = deviceid.replace('b\'', '')
            deviceid = deviceid.replace('\'', '')

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

                # print(url)
                print(response.text)

                # utime.sleep(0.25)

                response.close()
            except:
                print('Fail www connect...')
            # Save some cycles

        np.write()


main()
