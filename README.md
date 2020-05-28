
# Welcome to Infpyng  !
  
## Introduction  
  
***Infpyng*** is a powerful python script which use [fping](https://fping.org/) to probe endpoint through ICMP and parsing the output to [Influxdb](https://github.com/influxdata/influxdb). The result can then be visualize easily through [Grafana](https://grafana.com/).  
- ***Infpyng*** is perhaps your alternative to SmokePing
- You can add ***dynamic*** hosts without restarting script
- Custom ***Polling*** time configuration
- ***Low resource*** consumption
- ***Docker*** compatibility
  
**Benchmark**  
  
Those tests were performed from CentOS 8 with 1 CPU and 2 GB of memory  
| IP to ping | IP reachable | Finished in |
| :--- | :--- | :--- |
| 474 | 454 | 11 seconds |
| 1299 | 1197 | 13 seconds |
| 2653 | 2552 | 28 seconds |
| 3388 | 3262 | 32 seconds |

**Screenshots**  
![alt text](ping-monitor-infpyng.png) 
  
## Requirements
- Grafana 6.7.x  
  - Plugin : [grafana-multibar-graph-panel](https://github.com/CorpGlory/grafana-multibar-graph-panel)  
- Influxdb 1.8.x  
   
  
## Installation

The basic configuration is embedded in the image of the Docker you will have to create the files config.toml and hosts.toml from your host which will then have to be pushed in the image.

The `config.toml` file will contain your custom settings and especially the hostname/user/pass of your **InfluxDB**.

The hosts.toml file will have the list of all the hosts to ping.

> **Note:** For the following commands remember to adapt the tag version (example: **infpyng:1.0.0**) according to the image of the docker you are using.

### Docker usage
1. Pull the image from hub.docker
`docker pull oijkn/infpyng:1.0.0`

2. Create a container from the image called infpyng-tmp
`docker create --name infpyng-tmp oijkn/infpyng:1.0.0`

3. Run the copy command on the container to add your config/hosts files
`docker cp /path/from/your/host/config.toml infpyng-tmp:/app/infpyng/config`
`docker cp /path/from/your/host/hosts.toml infpyng-tmp:/app/infpyng/config`

4. Commit the container as a new image
`docker commit infpyng-tmp oijkn/infpyng:1.0.0`

5. Run the new image with your config files
`docker run -d -it --name infpyng -h docker-infpyng oijkn/infpyng:1.0.0`

> **Optional:** You can delete the temporary image you just created.
> // Get the CONTAINER ID
> docker ps -a
> // Remove it from Docker
> docker rm 53191e1f1408

#### SSH to Infpyng Docker

The command started using `docker exec` only runs while the container’s is running, and it is not restarted if the container is restarted.

1. Retrieve container id
`docker ps -a`

| CONTAINER ID | IMAGE | COMMAND | CREATED | STATUS | PORTS | NAMES |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **5591dbd111e5** | oijkn/infpyng:1.0.0 | `"python infpyng.py"` | 13 seconds ago | Up 11 seconds | | infpyng |

2. Retrieve container id
`docker exec -it 5591dbd111e5 sh`

3. Show log file
	```
	/app/infpyng # cat /var/log/infpyng.log
	2020-05-28 08:54:16 root INFO :: Settings loaded successfully
	2020-05-28 08:54:16 root INFO :: Init InfluxDB successfully
	2020-05-28 08:54:16 root INFO :: Starting Infpyng Multiprocessing v1.0.0
	2020-05-28 08:54:16 root INFO :: Polling time every 300s
	2020-05-28 08:54:16 root INFO :: Total of targets : 5
	2020-05-28 08:54:16 root INFO :: Multiprocessing : 40
	2020-05-28 08:54:16 root INFO :: Buckets : 5
	2020-05-28 08:54:20 root INFO :: Targets alive : 5
	2020-05-28 08:54:20 root INFO :: Targets unreachable : 0
	2020-05-28 08:54:20 root INFO :: Data written to DB successfully
	2020-05-28 08:54:20 root INFO :: Finished in : 4.44 seconds
	2020-05-28 08:54:20 root INFO :: ---------------------------------------
	```
  
### Github usage  

1. Download Infpyng project
	```  
	cd /somewhere/in/your/host
	git clone https://github.com/oijkn/infpyng.git  
	pip install -r requirements.txt  
	```
2. Ensure correct permission on \*.py files
`chmod -R +x /somewhere/in/your/host/infpyng/*.py`
  
3. Edit your custom settings  (conf + hosts)
`vi /somewhere/in/your/host/infpyng/config/config.toml`
`vi /somewhere/in/your/host/infpyng/config/hosts.toml`
  
  4. Run Infpyng python script
  `python infpyng.py &`

  
## Logger  

By default the Infpyng logs are located in */var/log/infpyng.log*

```
2020-05-26 09:19:41 root INFO :: Settings loaded successfully
2020-05-26 09:19:41 root INFO :: Init InfluxDB successfully
2020-05-26 09:19:41 root INFO :: Starting Infpyng Multiprocessing v1.0.0
2020-05-26 09:19:41 root INFO :: Polling time every 300s
2020-05-26 09:19:41 root INFO :: Total of targets : 1883  
2020-05-26 09:19:41 root INFO :: Multiprocessing : 40  
2020-05-26 09:19:41 root INFO :: Buckets : 47  
2020-05-26 09:19:51 root INFO :: Targets alive : 1883  
2020-05-26 09:19:51 root INFO :: Targets unreachable : 0  
2020-05-26 09:19:51 root INFO :: Data written to DB successfully  
2020-05-26 09:19:51 root INFO :: Finished in : 9.94 seconds  
```  
  
## Metrics  
 ### Format 
- infpyng  
  - tags:  
    - host (host name)  
    - target  
  - fields:  
    - packets_transmitted (integer)  
    - packets_received (integer)  
    - percent_packets_loss (float)  
    - average_response_ms (float)  
    - minimum_response_ms (float)  
    - maximum_response_ms (float)

### Architecture
```mermaid
graph LR
A[Metrics]  -->|Pull| B(Infpyng)
B -->|Push| C((InfluxDB))
C -->|Query| D{Grafana}
```
  
### Example Output  
```  
infpyng,country=de,host=TIG,server=germany,target=facebook.de average_response_ms=21.2,maximum_response_ms=21.8,minimum_response_ms=20.7,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000  
```  
  
## Github contributors lib  
- [High performance ping tool](https://github.com/schweikert/fping)  
- [Python lib for TOML](https://github.com/uiri/toml)  
- [Python client for InfluxDB](https://github.com/influxdata/influxdb-python)  
  
## Licensing  
  
This project is released under the terms of the MIT Open Source License. View LICENSE file for more information.
