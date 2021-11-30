"""Main module."""
import os
import time
import queue
import signal
import threading
import logging
import logging.config
import Adafruit_DHT

from configparser import Error
from os import kill, path
from threading import Thread

# Import our packets

from datetime import date, datetime, timedelta
from bot import run_bot
from fan import set_status
from relay.relay_controller import relay_clear
from outputs.rpi_publisher import mqtt_publisher

# Logger setup

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('MAIN')

# DHT11 settings -> should put these in .env file

sensor = 11
gpio = 4

# Thread 1
# get temp and hum from DHT11
# calls fan.set_status -> turns on the fan if temperature is over a range
# FAN IS TURNED OFF after some time -> it can be manually turned off with the override - could be cool to implement an "OFF for X minutes"
# calls outputs.rpi_publisher.mqtt_publisher to send temp and humidity via MQTT to the database
# it has a default shutdown procedure for a clear exit

def DHT11_Fan_caller(c, stop_event):
    item = [False, datetime.fromtimestamp(0)]
    c.put(item)
    counter = 0
    while not stop_event.wait(1):
        actual = c.get()

        try:
            # Reads Temperature and Humidity

            humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)

            if temperature > 10:
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

            if counter > 10:
                logger.critical("Failed DHT11 more than 10 times in a row - Shutting DOWN!")
                os.kill(os.getpid(), signal.SIGTERM)
            
            continue
        except Error as e:
            # Manage "not connected error"
            # Killing for safety: board could be shorted

            logger.critical(e)
            logger.critical("Failed DHT11 - is it connected?")
            logger.critical("Failed DHT11 - Shutting DOWN!")
            os.kill(os.getpid(), signal.SIGTERM)

        logger.debug("Sleeping for 2 seconds")
        time.sleep(2)
    
    # Called when the thread is killed
    # Clears Fifo Queue

    logging.info("Shutting Down DHT11_Fan_caller process")
    with c.mutex:
        logging.debug("Clearing Fifo Queue")
        c.queue.clear()

    #Clears Raspberry I/O

    logging.debug("Calling relay_clear I/O")
    relay_clear()


# ""MAIN""

def start():
    # SIGUSR1 handler. Used to gently kill thread 1 when SIGINT or SIGTERM are called
    # SIGUSR1 is sent from bot 

    def sigusr1_handler(*args):
        logging.debug(
            "Signal SIGUSR1 Received - Killing DHT11_Fan_caller process ")
        
        pill2kill.set()

        # wait for t1 to end
        t1.join()
        
        # kill the rest of the program
        logging.debug("Killing main module")
        kill(os.getpid(), signal.SIGTERM)

    signal.signal(signal.SIGUSR1, sigusr1_handler)

    pill2kill = threading.Event()
    q = queue.Queue()

    t1 = Thread(target=DHT11_Fan_caller, args=(q, pill2kill))
    t1.start()
    run_bot(q)


start()
