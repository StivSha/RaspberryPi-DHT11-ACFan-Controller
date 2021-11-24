import RPi.GPIO as GPIO
import time
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('relay_controller')

LED_PIN = 17


GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


def relay_on():
    logging.info("FAN ON")
    GPIO.output(LED_PIN, GPIO.HIGH)


def relay_off():
    logging.info("FAN OFF")
    GPIO.output(LED_PIN, GPIO.LOW)


def relay_clear():
    logging.info("CleanUP")
    GPIO.cleanup()
