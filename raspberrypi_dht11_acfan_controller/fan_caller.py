import time
import Adafruit_DHT
import logging
from datetime import date, datetime, timedelta
from configparser import Error
from fan import set_status
from relay.relay_controller import relay_clear
from outputs.rpi_publisher import mqtt_publisher
import os
import signal

sensor = 11
gpio = 4

logger = logging.getLogger("fan_caller")


# Thread 1
# get temp and hum from DHT11
# calls fan.set_status -> turns on the fan if temperature is over a range
# FAN IS TURNED OFF after some time -> it can be manually turned off with the override - could be cool to implement an "OFF for X minutes"
# calls outputs.rpi_publisher.mqtt_publisher to send temp and humidity via MQTT to the database
# it has a default shutdown procedure for a clear exit


def DHT11_Fan_caller(c, stop_event):
    '''
    c = queue, stop_event is used to tell the script when to shutdown gracefuly.
    
    When function is called a default fan status is added in the queue: [False, datetime.fromtimestamp(0)]
    The function exits when stop_event == 0 -> only if bot.py sends sigint1 -> fan_caller uses the shutdown procedure (clears queue and relay GPiO).
    As DHT11 sensors are difficult to read the reading procedure is in a try/catch expression. If temperature/humidity are not none and temp is >20 celsius
    the fan is automatically turned on for default time (8s) else it's turned off.
    '''

    item = [False, datetime.fromtimestamp(0)]
    c.put(item)

    while not stop_event.wait(1):
        logger.debug("Wait elapsed")
        actual = c.get()

        try:
            logger.debug("Reading DHT11")
            humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)

            if (temperature is not None) and (humidity is not None):
                # Reads Temperature and Humidity

                if temperature > 20:
                    c.put(set_status(status=True, actual=actual))
                    logger.debug("Status ON")
                else:
                    # used only to call set_status and pass actual data

                    c.put(set_status(status=False, actual=actual))
                    logger.debug("Status OFF")

                logger.debug("Publishing MQTT")
                mqtt_publisher(temp=temperature, hum=humidity)
            else:
                c.put(item)
                logger.critical("Unreadable DHT11 - adding %s in queue" %item)

        except RuntimeError as e:
            logger.critical(e) 
            logger.critical("Failed DHT11 - is it connected?") 
            logger.critical("Failed DHT11 - Shutting DOWN!")
            os.kill(os.getpid(), signal.SIGTERM)

        logger.debug("Sleeping for 20 seconds")
        time.sleep(20)

    # Called when the thread is killed
    # Clears Fifo Queue
    logger.info("Shutting Down DHT11_Fan_caller process")
    with c.mutex:
        logger.debug("Clearing Fifo Queue")
        c.queue.clear()

    # Clears Raspberry I/O -> GPiO - relay.relay_controller import relay_clear
    logger.debug("Calling relay_clear I/O")
    relay_clear()
