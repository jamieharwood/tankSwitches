from machine import Pin
import machine
import utime
import varibles as vars

functionSelectPin = Pin(0, Pin.IN, Pin.PULL_UP)  # D3
waterOnPin = Pin(2, Pin.IN, Pin.PULL_UP)  # D4

powerLedPin = Pin(4, Pin.OUT)  #D2
functionLedPin = Pin(5, Pin.OUT)  #D1
waterLedPin = Pin(15, Pin.OUT)  # D8


def pinCallback(p):
    irqState = machine.disable_irq()
    utime.sleep_ms(100)
    
    #print('Button state change, pin ',  p)
    # Read switch inputs
    vars.functionSelect = functionSelectPin.value()
    vars.waterOn = waterOnPin.value()

    # Check against the last input
    if ( vars.functionSelect != vars.functionSelectLast ):
        #vars.sendFunctionChange = True
        if (vars.functionSelect == True):
            functionLedPin.off()
        else:
            functionLedPin.on()

        vars.functionSelectLast = vars.functionSelect  # Set the last pointers
        print('if ( functionSelect != functionSelectLast ):')
    #else:
        #vars.sendFunctionChange = False

    if ( vars.waterOn != vars.waterOnLast ):
        #vars.sendWaterChange = True
        if (vars.waterOn == True):
            waterLedPin.off()
        else:
            waterLedPin.on()

        vars.waterOnLast = vars.waterOn  # Set the last pointers
        print('if ( waterOn != waterOnLast ):')
    #else:
        #vars.sendWaterChange = False

    machine.enable_irq(irqState)

def main():
    # Set initial state
    powerLedPin.on()
    functionLedPin.off()
    waterLedPin.off()
    
    vars.functionSelect = functionSelectPin.value()
    vars.waterOn = waterOnPin.value()
    
    if (vars.functionSelect == True):
        functionLedPin.off()
    else:
        functionLedPin.on()
    
    if (vars.waterOn == True):
        waterLedPin.off()
    else:
        waterLedPin.on()
    
    # Set callnack routines
    functionSelectPin.irq(trigger=Pin.IRQ_RISING, handler=pinCallback)
    waterOnPin.irq(trigger=Pin.IRQ_RISING, handler=pinCallback)

    while True:
        # Save some cycles
        utime.sleep_ms(500)

main()


