import machine
import time

functionSelect = 0
functionSelectLast = -1
waterOn = 0
waterOnLast = -1
    
functionSelectPin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
waterOnPin = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
powerLedPin = machine.Pin(3, machine.Pin.OUT)

powerLedPin.on()
   
while True:
    functionSelect = functionSelectPin.value()
    waterOn = waterOnPin.value()
    
    if ( functionSelect != functionSelectLast ):
        functionSelectLast = functionSelect
        
    if ( waterOn != waterOnLast ):
        waterOnLast = waterOn

    time.sleep(0.25)
