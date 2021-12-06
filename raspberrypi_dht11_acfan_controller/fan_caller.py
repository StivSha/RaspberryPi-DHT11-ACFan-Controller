import time
import Adafruit_DHT
import logging
from datetime import date, datetime, timedelta
from configparser import Error
from fan import set_status
from relay.relay_controller import relay_clear
from outputs.rpi_publisher import mqtt_publisher
import os
#import queue
import signal

sensor = 11
gpio = 4

logger = logging.getLogger('fan_caller')

def DHT11_Fan_caller(c, stop_event):
    item = [False, datetime.fromtimestamp(0)]
    c.put(item)
    counter = 0

    # print("DHT11 ready")
    while not stop_event.wait(1):
        actual = c.get()

        try:
            # Reads Temperature and Humidity

            humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)

            if temperature > 25:
                c.put(set_status(status=True, actual=actual))
                logger.debug("Status ON")
            else:
                # used only to call set_status and pass actual data

                c.put(set_status(status=False, actual=actual))
                logger.debug("Status OFF")

            logger.debug("Publishing MQTT")
            mqtt_publisher(temp=temperature, hum=humidity)
            counter = 0
        except RuntimeError as e:
            # As DHT11 sensors are not reliable, this is needed. If data is not read for more than 10 times in a row, program gets shut down
            counter = counter + 1
            logger.critical(e)
            logger.critical("Failed to read DHT11")

            if counter > 25:
                logger.critical(
                    "Failed DHT11 more than 10 times in a row - Shutting DOWN!")
                os.kill(os.getpid(), signal.SIGTERM)

            continue
        except Error as e:
            # Manage "not connected error"
            # Killing for safety: board could be shorted

            logger.critical(e)
            logger.critical("Failed DHT11 - is it connected?")
            logger.critical("Failed DHT11 - Shutting DOWN!")
            os.kill(os.getpid(), signal.SIGTERM)

        # print("autostuff sleeping for 20 secs")
        logger.debug("Sleeping for 180 seconds")
        time.sleep(180)

    # Called when the thread is killed
    # Clears Fifo Queue
    logger.info("Shutting Down DHT11_Fan_caller process")
    with c.mutex:
        logger.debug("Clearing Fifo Queue")
        c.queue.clear()

    # Clears Raspberry I/O

    logger.debug("Calling relay_clear I/O")
    relay_clear()