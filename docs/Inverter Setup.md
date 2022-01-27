# MPP Solar Inverter - Connecting to local MQTT / Influx / Grafana #

Connecting to Grafana, as documented below uses a number of components / steps.

## Requirements
```
sudo apt install python3-pip  
sudo pip3 install bluepy  
sudo pip3 install paho-mqtt  
```
## Install Mpp-Solar
Stable version:
`sudo pip3 install mpp-solar`  

#### TEST MPP-SOLAR

After installing mpp-solar check the cable connection with dmesg to know where it’s mounted (default /ttyUSB0 ).

run:
```
	mpp-solar -p /dev/ttyUSB0 -c QPI
```
output should be
```
Command: QPI - Protocol ID inquiry
------------------------------------------------------------
Parameter                     	Value           Unit
protocol_id                   	PI30
```
to get more infos add -I or -D flags.

To get help use: `mpp-solar --help`  
  To get help about some commands use (for example)
`mpp-solar -o`
it will list all outputs.

To get readings from the inverter use:   
`mpp-solar -p /dev/ttyUSB0 -c QPIGS`

### Install Mosquitto
It’s an MQTT Broker.
```
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service
sudo systemctl start mosquitto.service
```
### Test Mosquitto
* In CMD1:  
	`  mosquitto_sub -h localhost -v -t "#" `
* In CMD2:  
	` mosquitto_pub -h localhost -t "basetopic/subtopic" -m "this is the message" `  
* In CMD1 output should be:
  ```
  $ mosquitto_sub -h localhost -v -t "#"
  basetopic/subtopic this is the message
  ```
* In CMD2 test with (it outputs data in json):  
	` mpp-solar -q localhost -c QID -o json_mqtt`
* In CMD1 output should be something like this:
  ```
  mpp-solar {"ac_input_voltage": 234.6, "ac_input_frequency": 49.9, "ac_output_voltage": 234.6, "ac_output_frequency": 49.9, "ac_output_apparent_power": 400, "ac_output_active_power": 251, "ac_output_load": 8, "bus_voltage": 401, "battery_voltage": 49.5, "battery_charging_current": 0, "battery_capacity": 73, "inverter_heat_sink_temperature": 37, "pv_input_current_for_battery": 0.0, "pv_input_voltage": 0.0, "battery_voltage_from_scc": 0.0, "battery_discharge_current": 0, "is_sbu_priority_version_added": 0, "is_configuration_changed": 0, "is_scc_firmware_updated": 0, "is_load_on": 1, "is_battery_voltage_to_steady_while_charging": 0, "is_charging_on": 0, "is_scc_charging_on": 0, "is_ac_charging_on": 0}
  ```

### Setup Cron
```
crontab -e
* * * * * /usr/local/bin/mpp-solar -o json_mqtt -q localhost -c QPIGS -i > /home/pi/cron.out 2>&1
```
we got problems with this command: outputs different from json_mqtt weren’t correctly imported by the DB.

### INSTALL GRAFANA
NOTE: Traefik not needed, but suggested.

```
version: '3.7'
services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    user: '472'
    environment:
      - GF_SERVER_ROOT_URL=https://grafana.<YOUR DOMAIN>
      - GF_EXTERNAL_IMAGE_STORAGE=local
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    networks:
      - default
      - proxy
    volumes:
      - ./grafana-storage:/var/lib/grafana
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=proxy"
      - "traefik.http.routers.grafana-secure.entrypoints=websecure"
      - "traefik.http.routers.grafana-secure.rule=Host(`grafana.<YOUR DOMAIN>`)"
      - "traefik.http.routers.grafana-secure.service=grafana-service"
      - "traefik.http.services.grafana-service.loadbalancer.server.port=3000"

networks:
  proxy:
    external: true
```
Where `proxy` is your Traefik network and `user: '472'` needs root permissions [Grafana DOCS](https://grafana.com/docs/grafana/latest/installation/docker/).
You'll need to add InfluxDB's IP to the datasources:
```
URL: http://<INFLUXDB IP>:8070
Database: mppsolar
User: grafana
Password: <YOUR-GRAFANA-PASSWORD>
```
you'll set it in next part.  
You can import the dashboard: `RwyrrtD7z1234`

### Install InfluxDB
```
mkdir influxdb
chmod 777 influxdb #or at least drwxrwxr-x
```
At the moment InfluxDB is setup using Docker Run, in the future a Docker File will be provided.
```
docker run --name=influxdb --env=INFLUXDB_ADMIN_USER=<ADMIN USER NAME> --env=INDLUXDB_ADMIN_PASSWORD=<ADMIN PWD> --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --env=INFLUXDB_VERSION=1.8.3 --volume=influxdb_data:/var/lib/influxdb --volume=/var/lib/influxdb --network=grafana_default -p 8070:8086 --restart=always --runtime=runc --detach=true influxdb:1.8.3 influxd
```

##### Configure
* Open InfluxDB bash
` docker exec -it influxdb bash `
* Run `influx`
```
create database mppsolar
use mppsolar
create user grafana with password '<passwordhere>' with all privileges
grant all privileges on dht11 to grafana
show users
```
* output should be

```
user admin
---- ----
grafana true
```
* then `exit`



### Install and Setup Telegraf
#### Install and Configure Telegraf
* ` sudo apt-get install telegraf `

###### Configure
* go to ` /etc/telegraf`
* open with an editor ` telegraf.conf `; it uses toml format
* find ` [[inputs.mqtt_consumer]] `
* add a new topic
```
[[inputs.mqtt_consumer]]
  servers = ["tcp://127.0.0.1:1883"]
  topics = [
    "mpp-solar",
  ]
  data_format = "json"
  [inputs.mqtt_consumer.tags]
    destinationdb = "db01"
```
  * servers = ... : it means localhost
  * topics: it's mpp-solar.. MQTT topics  
  * destinationdb: it's the designed db to store this data, see more next


* find `OUTPUT PLUGINS`
```
[[outputs.influxdb]]
  urls = ["http://<YOUR DB IP>:8070"]
  database = "mppsolar"
  skip_database_creation = true
  username = "grafana"
  password = "<YOUR PWD>"
  tagexclude = ["destinationdb"]
  [outputs.influxdb.tagpass]
    "destinationdb" = ["db01"]
```
  * urls-port is `8070`, the same of InfluxDB docker-run
  * `tagexclude ... ["db01"]` used to have multiple outputs to the same DB  
_NOTE: indentation is important as it's a TOML file_

###### Start Telegraf at boot
```
sudo systemctl unmask telegraf.service
sudo systemctl start telegraf
sudo systemctl enable telegraf.service
```

To read Telegraf Logs use
`sudo systemctl status telegraf`
