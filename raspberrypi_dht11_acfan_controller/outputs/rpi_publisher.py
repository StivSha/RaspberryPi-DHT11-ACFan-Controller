import json
import logging
import logging.config
import paho.mqtt.publish as publish


# Setting right logger

logger = logging.getLogger('rpi_publisher')


# Publishing and Logging MQTT
# Database used is InfluxDB: timestamp isn't needed
# Publishing format is in JSON 

def mqtt_publisher(temp, hum):
    
    try:
        data_set = {"temperature": temp, "humidity": hum}
        json_dump = json.dumps(data_set)
        publish.single("TempHumSens", json_dump, qos=0,
                       retain=False, hostname="localhost", port=1883)

        logger.info(f"Correct Publishing")

    except Exception as e:
        logger.error(f"Error publishing MQTT messages to broker")
        logger.error(e)


if __name__ == '__main__':
    mqtt_publisher(1,2)
    print("MQTT CLIENT should print 1,2 with topic = 'TempHumSens'")
