from machine import Pin
import machine
import utime
import varibles as vars
import neopixel


functionSelectPin = Pin(0, Pin.IN, Pin.PULL_UP)  # D3
waterOnPin = Pin(2, Pin.IN, Pin.PULL_UP)  # D4

powerLedPin = Pin(4, Pin.OUT)  #D2
functionLedPin = Pin(5, Pin.OUT)  #D1
waterLedPin = Pin(15, Pin.OUT)  # D8

def main():
    np = neopixel.NeoPixel(machine.Pin(12), 4)
    
    # Set initial state
    np[0] = (255,  0,  0)
    powerLedPin.on()
    functionLedPin.off()
    waterLedPin.off()
    
    vars.functionSelect = functionSelectPin.value()
    vars.waterOn = waterOnPin.value()
    
    if (vars.functionSelect == True):
        np[1] = (0,  0,  0)
        functionLedPin.off()
    else:
        np[1] = (0,  255,  0)
        functionLedPin.on()
    
    if (vars.waterOn == True):
        np[2] = (0,  0,  0)
        waterLedPin.off()
    else:
        np[2] = (0,  255,  0)
        waterLedPin.on()

    while True:
        # utime.sleep_ms(100)
    
        #print('Button state change, pin ',  p)
        # Read switch inputs
        vars.functionSelect = functionSelectPin.value()
        vars.waterOn = waterOnPin.value()
    
        # Check against the last input
        if ( vars.functionSelect != vars.functionSelectLast ):
            if (vars.functionSelect == True):
                np[1] = ( 0,  0,  0)
                functionLedPin.off()
            else:
                np[1] = ( 0,  255,  0)
                functionLedPin.on()
    
            vars.functionSelectLast = vars.functionSelect  # Set the last pointers
            print('if ( functionSelect != functionSelectLast ):')
    
        if ( vars.waterOn != vars.waterOnLast ):
            if (vars.waterOn == True):
                np[2] = ( 0,  0,  0)
                waterLedPin.off()
            else:
                np[2] = ( 0,  255,  0)
                waterLedPin.on()
    
            vars.waterOnLast = vars.waterOn  # Set the last pointers
            print('if ( waterOn != waterOnLast ):')

        # Save some cycles
        utime.sleep_ms(200)

main()


