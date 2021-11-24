from paho import mqtt
import paho.mqtt.publish as publish
import logging
import logging.config
import json

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('rpi_publisher')


def mqtt_publisher(temp, hum):

    # Publishing and Logging MQTT
    # Database used is InfluxDB: timestamp isn't needed
    try:
        data_set = {"temperature": temp, "humidity": hum}
        json_dump = json.dumps(data_set)
        publish.single("TempHumSens", json_dump, qos=0,
                       retain=False, hostname="localhost", port=1883)
        #publish.single("TempHumSens", str(temp) + " " + str(hum), qos=0, retain=False, hostname="localhost", port=1883)
        logger.info(f"Correct Publishing")
    except Exception as e:
        logger.error(f"Error publishing MQTT messages to broker")
        logger.error(e)

# mqtt_publisher(1,2)
