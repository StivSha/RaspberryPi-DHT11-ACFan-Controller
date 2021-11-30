import RPi.GPIO as GPIO
import logging


# Setting right logger

logger = logging.getLogger('relay_controller')


# Setting FAN_PIN -> should put this in .env file

FAN_PIN = 17


# Statc GPIO - maybe put this in __init__ for clarity

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)


# Set ""HIGH"" status on FAN_PIN

def relay_on():
    logger.info("FAN ON")
    GPIO.output(FAN_PIN, GPIO.HIGH)


# Set ""LOW"" status on FAN_PIN

def relay_off():
    logger.info("FAN OFF")
    GPIO.output(FAN_PIN, GPIO.LOW)


# Used at exit for cleaning IO Ports

def relay_clear():
    logger.info("Cleaning Raspberry IO ports")
    GPIO.cleanup()
