Multi-container Docker app built from the following services:

* [InfluxDB](https://github.com/influxdata/influxdb) - time series database
* [Chronograf](https://github.com/influxdata/chronograf) - admin UI for InfluxDB
* [Grafana](https://github.com/grafana/grafana) - visualization UI for InfluxDB

Useful for quickly setting up a monitoring stack for performance testing. Combine with [Infpyng](https://github.com/oijkn/infpyng) to create a performance testing environment in minutes.

## Quick Start

To start the app:

1. Install [docker-compose](https://docs.docker.com/compose/install/) on the docker host.
1. Clone this [repo](https://github.com/oijkn/infpyng) on the docker host.
1. Run the following command from the `infpyng-stack` directory of the cloned repo:
```sh
sh run.sh
```

To stop the app:

1. Run the following command from the `infpyng-stack` directory of the cloned repo:
```sh
sh stop.sh
```

To remove all images/containers:

1. Run the following command from the `infpyng-stack` directory of the cloned repo:
```sh
sh clear_all.sh
```
> **Warning:** This will remove all the images and containers from your docker created by Infpyng

## Ports

The services in the app run on the following ports:

| Host Port | Service |
| - | - |
| 3000 | Grafana |
| 8086 | InfluxDB |
| 8888 | Chronograf |

Note that Chronograf does not support username/password authentication. Anyone who can connect to the service has full admin access.

## Volumes

The app creates the following named volumes (one for each service) so data is not lost when the app is stopped:

* data/influxdb
* data/chronograf
* data/grafana

## Users

The app creates one admin user for Grafana. By default, the username and password of this account is `admin`.

## Database

The app creates a default InfluxDB database called `infpyng`.

## Data Sources

The app creates a Grafana data source called `InfluxDB` that's connected to the defaultIndfluxDB database.

## Dashboards

By default, the app create a Grafana dashboards from my [example](https://github.com/oijkn/infpyng/blob/master/dashboard-grafana/dashboard-grafana.json) that's configured to work with [Infpyng](https://github.com/oijkn/infpyng).

