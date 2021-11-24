from configparser import Error
import sys
import signal
from typing import Tuple
import Adafruit_DHT
from fan_automatic_temp import set_status
from rpi_publisher import mqtt_publisher
import time
import logging
import logging.config
from relay_controller import relay_clear

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('DHT11_controller')
# for DHT11

# aggiungere i controlli
'''
TODO
1.  fare un controllo che quando il programma esegue, ma il dht11 non risponde vengono disattivate le porte per il rele'
    quindi fare un try/catch qui sotto nel while. se dht11 non risponde dopo aver disattivato le porte, uccide il programma.

2.  telegraf setup

3.  telegram setup

4.  (i forgot)

'''

# good boy helping in case of process killed


def sigint_handler(signal, frame):
    logger.critical("Interrupted")
    logger.critical("Setting forced status to false")
    set_status(status=False)
    relay_clear()
    logger.critical("Exiting")
    print('Interrupted')
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGKILL, sigint_handler)
sensor = 11

gpio = 4


'''
if humidity is not None and temperature is not None:
  print(f'Temperature: {temperature:0.1f} C Humidity: {humidity:0.1f}')
else:
  print ("Failed to get reading. Check the sensor connection!")
'''
# attivare con umidita' relativa
# mettere un while true e un print e sleep
while True:
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)

        if temperature > 10:
            set_status(status=True)
            logger.debug("Status ON")
        else:
            set_status(status=False)
            logger.debug("Status OFF")

        #logger.debug("Publishing MQTT")
        #mqtt_publisher(temp=temperature, hum=humidity)

    except RuntimeError as e:
        logger.critical(e)
        logger.critical("Failed to read DHT11")
        continue
    except Error as e:
        logger.critical(e)
        logger.critical("Failed DHT11 - is it connected?")
        signal.SIGINT

    logger.debug("Sleeping for 2 seconds")
    time.sleep(2)
