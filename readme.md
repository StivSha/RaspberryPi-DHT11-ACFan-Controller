# About this project
RaspberryPi-DHT11-ACFan-Controller is a simple automatic fan controller for RasperryPi's GPiO library. It uses a DHT11 to get temperature and humidity and sends this data with MQTT to a database. The relay is automatically set to True when temperature > something static, but it can be overrided by the Telegram bot.

### Requirements
Simply run
`pip3 install -r requirements.txt ` from RaspberryPi-DHT11-ACFan-Controller directory.

If `pip3` is not installed run `python3 install pip3`.

### Configuring and Usage

#### Download the repository
Clone this repository from GitHub

```
git clone https://github.com/sa1g/RaspberryPi-DHT11-ACFan-Controller

```

#### Setup Telegram's API KEY
If you don't have one already, [create a Telegram Bot](https://core.telegram.org/bots).
Then:
```
cd /path/to/RaspberryPi-DHT11-ACFan-Controller/RaspberryPi-DHT11-ACFan-Controller
mkdir remote & cd remote
nano key.py
```
paste and add your key:
`API_KEY = '<YOU API KEY>'`
save with **CTRL+X**.

#### Install and test MQTT
###### Install

* Install Mosquitto ``` sudo apt install -y mosquitto mosquitto-clients ```

* Set MQTT service to start on boot ``` sudo systemctl enable mosquitto.service ```

* Start MQTT service ``` sudo systemctl start mosquitto.service ```

###### Test
You'll need to use two different bash terminals (called here B1 and B2 for clarity).  
* **B1**: ``` mosquitto_sub -h localhost -v -t "#" ```
    TODO: add a little bit of mosquitto flags meaning

    -t: MQTT's message topic
    -v: verbose
    -h: host
* **B2**: go to RaspberryPi-DHT11-ACFan-Controller's directory and execute ```python3 /test/mqtt.test.py  ```
* output should be:
```
TODO create decent output here
```

#### Install and Configure Grafana (Docker & Traefik)
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
Where `proxy` is your Traefik network and `user: '472'` needs have root permissions [Grafana DOCS](https://grafana.com/docs/grafana/latest/installation/docker/).

You can import the dashboard: `Nnmekrc7z`

#### Install and Configure InfluxDB (Docker)
###### Install
```
mkdir influxdb
chmod 777 influxdb #or at least drwxrwxr-x
```
At the moment InfluxDB is setup using Docker Run, in the future a Docker File will be provided.
```
docker run --name=influxdb --env=INFLUXDB_ADMIN_USER=<ADMIN USER NAME> --env=INDLUXDB_ADMIN_PASSWORD=<ADMIN PWD> --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --env=INFLUXDB_VERSION=1.8.3 --volume=influxdb_data:/var/lib/influxdb --volume=/var/lib/influxdb --network=grafana_default -p 8070:8086 --restart=always --runtime=runc --detach=true influxdb:1.8.3 influxd
```

###### Configure
* Open InfluxDB bash
` docker exec -it influxdb bash `
* Run `influx`
```
create database dht11
use dht11
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
    "TempHumSens"
  ]
  data_format = "json"
  [inputs.mqtt_consumer.tags]
    destinationdb = "db02"
```
  * topics: it's RaspberryPiDHT11.. MQTT topics  
  * destinationdb: it's the designed db to store this data  


* find `OUTPUT PLUGINS`
```
[[outputs.influxdb]]
  urls = ["http://<IP of InfluxDB database>:8070"]
  database = "dht11"
  skip_database_creation = true
  username = "grafana"
  password = "<your-passwordhere>"
  tagexclude = ["destinationdb"]
  [outputs.influxdb.tagpass]
    "destinationdb" = ["db02"]
```
  * urls-port is `8070`, the same of the docker-run
  * `tagexclude ... ["db02"]` used to have multiple outputs to the same DB

###### Start Telegraf at boot
```
sudo systemctl unmask telegraf.service
sudo systemctl start telegraf
sudo systemctl enable telegraf.service
```

### Run RaspberryPi-DHT11-ACFan-Controller
//To run the program in the background:  
//`nohup python3 raspberrypi_dht11_acfan_controller/raspberrypi_dht11_acfan_controller.py`

Run RaspberryPi-DHT11-ACFan-Controller at system-boot. Precisely after home mount  
```
TODO: NEEDS TO BE TESTED
crontab -e
@reboot /path/to/RaspberryPi-DHT11-ACFan-Controller.py
```

To find its PID:  
`ps ax | grep raspberrypi_dht11_acfan_controller.py`  
