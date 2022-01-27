import RPi.GPIO as GPIO
import logging

# Setting right logger
#logger = logging.getLogger('relay_controller')

# maybe put this in __init__ for clarity
# Setting FAN_PIN -> should put this in .env file
FAN_PIN = 17

# also this
# Statc GPIO 
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

def relay_on():
    '''Set ""HIGH"" status on FAN_PIN '''

    #logger.info("FAN ON")
    GPIO.output(FAN_PIN, GPIO.HIGH)

def relay_off():
    '''Set ""LOW"" status on FAN_PIN'''

    #logger.info("FAN OFF")
    GPIO.output(FAN_PIN, GPIO.LOW)

def relay_clear():
    '''Used at exit for cleaning IO Ports'''

    #logger.info("Cleaning Raspberry IO ports")
    GPIO.cleanup()

