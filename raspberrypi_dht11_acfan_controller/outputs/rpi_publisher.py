import json
import logging
import logging.config
import paho.mqtt.publish as publish

# Setting right logger
logger = logging.getLogger('rpi_publisher')

# Database used is InfluxDB: timestamp isn't needed
# Publishing format: JSON

def mqtt_publisher(temp, hum):
    '''
    Publishes data via MQTT, in localhost on port 1883.
    temp = temperature value, hum = humidity value
    these 2 data will be pubished via MQTT in JSON.
    json_dump dumps these data as JSON.
    Publishing successes/errors are logged. 
    '''

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
    '''
    used for testing purposes, publishes 1,2 on mqtt_publisher defaults
    '''

    mqtt_publisher(1, 2)
    print("MQTT CLIENT should print 1,2 with topic = 'TempHumSens'")
