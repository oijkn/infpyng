# infpyng

## Introduction

***infpyng*** is a simple python script which utilize [fping](https://fping.org/) to probe endpoint through ICMP and parsing the output with [Telegraf - Exec Input Plugin](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec) to [Influxdb](https://github.com/influxdata/influxdb). The result can then be visualize through [Grafana](https://grafana.com/) with ease.
- ***infpyng*** is perhaps your alternative to SmokePing !

**Requirements**
- Python 3.x
- fping 4.x

**Screenshots**
![alt text](ping-monitor-infpyng.png)

## Installation
**Download infpyng project and place it inside /usr/local/bin/**
```
# cd /usr/local/bin/
# git clone https://github.com/oijkn/infpyng.git
# pip3 install toml
```

## Usage
**1. Ensure Correct Permission on \*.py files**
```
# chmod 755 /usr/local/bin/infpyng/*.py
```

**2. Configure global settings in /usr/local/bin/infpyng/config/config.toml**
```toml
[config]
name = "infpyng config"
description = "infpyng can ping multiple hosts at once and return statistics to Influxdb using Exec Input Plugin"
version = "0.0.1"

[options]
## Number of request packets to send to each target
count = 2

## The minimum amount of time in milliseconds between sending a ping packet
## to any target (default is 10ms, minimum is 1ms)
# interval = 100

## The time to wait for a ping response in milliseconds
## the default timeout is 500ms
timeout = 2000

## Backoff factor, this parameter is the value by which the wait time (-t) is
## multiplied on each successive request; it must be entered as a
## floating-point number (x.y). The default is 1.5.
backoff = 1.0

## Retry limit (default 3). This is the number of times an attempt at pinging
## a target will be made, not including the first try.
retry = 1

## Set the typ of service flag ( TOS ). N can be either decimal or
## hexadecimal (0xh) format.
tos = 0
```

**3. Configure host(s) file in /usr/local/bin/infpyng/config/hosts.toml**
```toml
# you can use several configuration files for the hosts by respecting the structure as follows
[[targets]]
  hosts = ['8.8.8.8', '8.8.4.4']
  [targets.tags]
     country = 'us'
     server = 'dns'

[[targets]]
  hosts = ['google.fr']
  [targets.tags]
     country = 'fr'
     server = 'french'

[[targets]]
  hosts = ['amazon.es']
  [targets.tags]
     country = 'es'
     server = 'spain'

[[targets]]
  hosts = ['facebook.de']
  [targets.tags]
     country = 'de'
     server = 'germany'
```

**4. Configure your Telegraf plugin**
```toml
# exmaple : /etc/telegraf/telegraf.conf
[[inputs.exec]]
    commands = ["/path/of/your/python3 /usr/local/bin/infpyng/infpyng.py"]
    interval = "300s"
    timeout = "300s"
    data_format = "influx"
```

**5. Testing the script**
```
# telegraf --config=/etc/telegraf/telegraf.conf--input-filter exec --test

2020-05-11T10:33:06Z I! Starting Telegraf 1.14.2
> infpyng,country=us,host=TIG,server=dns,target=8.8.8.8 average_response_ms=22.2,maximum_response_ms=22.3,minimum_response_ms=22.2,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000
> infpyng,country=us,host=TIG,server=dns,target=8.8.4.4 average_response_ms=21.4,maximum_response_ms=21.6,minimum_response_ms=21.2,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000
> infpyng,country=fr,host=TIG,server=french,target=google.fr average_response_ms=22.2,maximum_response_ms=22.3,minimum_response_ms=22,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000
> infpyng,country=es,host=TIG,server=spain,target=amazon.es average_response_ms=38.3,maximum_response_ms=38.4,minimum_response_ms=38.2,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000
> infpyng,country=de,host=TIG,server=germany,target=facebook.de average_response_ms=21.2,maximum_response_ms=21.8,minimum_response_ms=20.7,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000
```

## Metrics

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

### Example Output
```
infpyng,country=de,host=TIG,server=germany,target=facebook.de average_response_ms=21.2,maximum_response_ms=21.8,minimum_response_ms=20.7,packets_received=2i,packets_transmitted=2i,percent_packet_loss=0i 1589193188000000000
```

## Common Issues:

**My script works when I run it by hand, but not when Telegraf is running as a service.**
This may be related to the Telegraf service running as a different user. The official packages run Telegraf as the `telegraf` user and group on Linux systems. Resolved this with the following in sudoers:
```
telegraf ALL=(ALL) NOPASSWD: /path/of/your/python3
```
