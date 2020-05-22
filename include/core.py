# -*- coding: utf-8 -*-

import glob
import operator
import os
import socket
import logging
import requests
from influxdb import InfluxDBClient
from functools import reduce

import toml


class Infpyng:
    # set conf.toml file
    config = ''
    # set options
    count = int(1)
    interval = int(10)
    period = int(1000)
    timeout = int(500)
    backoff = float(1.5)
    retry = int(3)
    tos = int(0)
    # dict with all host -> tags
    dictags = {}
    # list for final result
    result = []
    # list of hots alive
    alive = []
    # default log file
    logfile = '/var/log/infpyng.log'
    # set InfluxDB
    hostname = 'localhost'
    port = 8086
    dbname = 'infpyng'
    user = ''
    pwd = ''

    def __init__(self):
        # set path where script is running
        self.path = os.path.realpath(
            os.path.join(os.getcwd(),
                         os.path.dirname(__file__))
        )
        # gracefully quit ProcessPoolExecutor
        self.bye = True

    def init_infpyng(self):
        self.set_conf()
        self.set_targets()
        self.set_influx()

    def set_conf(self):
        """ Loads infpyng configuration from a TOML file """
        self.config = toml.load(os.path.dirname(self.path) + "/config/config.toml")
        options = self.config['options']
        if 'count' in options:
            self.count = int(options['count'])
        if 'interval' in options:
            self.interval = int(options['interval'])
        if 'period' in options:
            self.period = int(options['period'])
        if 'timeout' in options:
            self.timeout = int(options['timeout'])
        if 'backoff' in options:
            self.backoff = float(options['backoff'])
        if 'retry' in options:
            self.retry = int(options['retry'])
        if 'tos' in options:
            self.tos = int(options['tos'])

    def set_logger(self):
        # set globs of all TOML files
        globs = glob.glob(os.path.dirname(self.path) + "/config/*.toml")
        if any("config.toml" in f for f in globs):
            self.config = toml.load(os.path.dirname(self.path) + "/config/config.toml")
            log = self.config['logging']
            if 'path' in log:
                self.logfile = str(log['path'])
            os.chmod(self.logfile, 0o644)
            return True

    def set_influx(self):
        self.config = toml.load(os.path.dirname(self.path) + "/config/config.toml")
        influx = self.config['influxdb']
        if 'hostname' in influx:
            self.hostname = str(influx['hostname'])
        if 'port' in influx:
            self.port = int(influx['port'])
        if 'dbname' in influx:
            self.dbname = str(influx['dbname'])
        if 'username' in influx:
            self.user = str(influx['username'])
        if 'password' in influx:
            self.pwd = str(influx['password'])

    def set_targets(self):
        """
        Loads targets from a TOML file(s) and prepare dict with
        all tags if they are set.
        """
        # set globs of all TOML files
        globs = glob.glob(os.path.dirname(self.path) + "/config/*.toml")
        # exclude config file from glob
        toml_files = [x for x in globs if "config.toml" not in x]

        # set list for all targets
        all_targets = []
        # loop in all file to find value(s) of 'hosts' keys
        for toml_file in toml_files:
            targets = toml.load(toml_file)
            list2d = self.find_keys(targets, 'hosts')
            all_targets = list(list2d) + all_targets

            # set dict with paired host -> tags
            items = (item for item in targets['targets'])
            for item in items:
                if 'tags' in item:
                    for host in item['hosts']:
                        self.dictags[host] = item['tags']

        # make flat list out of list of lists
        # --> https://stackoverflow.com/a/39493960
        all_targets = reduce(operator.concat, all_targets)

        return all_targets

    def inf_parse(self, data, timestamp):
        """
        Parse infpyng response from fping cmd.
        # '1.1.1.1 : xmt/rcv/%loss = 1/1/0%, min/avg/max = 1.35/1.35/1.35'
        # measurement_name,myhost=hostname1,mytag=server used=10.00 1589048898016737024
        """
        for line in data.splitlines():
            # get host and metrics
            [host, s_1] = line.split(" : ")
            # host is alive
            if s_1.find(',') != -1:
                [stats, ping] = s_1.split(", ")
                # get packet loss %
                [_, s_2] = stats.split(" = ")
                [sent, recv, loss] = s_2.split("/")
                # get latency
                [_, s_3] = ping.split(" = ")
                [min_, avg, max_] = s_3.split("/")

                # if tags is set
                if self.dictags.get(host.strip()) is not None:
                    item = self.dictags.get(host.strip()).items()
                    tags = ',' + ','.join(f'{key}={value}' for key, value in item)
                else:
                    tags = ''

                # prepare output for influxdb
                influx_output = ('infpyng,host=' + socket.gethostname() +
                                 ',target=' + host.strip() +
                                 tags +
                                 ' average_response_ms=' + avg +
                                 ',maximum_response_ms=' + max_ +
                                 ',minimum_response_ms=' + min_ +
                                 ',packets_received=' + recv + 'i' +
                                 ',packets_transmitted=' + sent + 'i' +
                                 ',percent_packet_loss=' + loss.strip('%') +
                                 ' ' + timestamp
                                 )
                # list with all alive hosts
                self.alive.append(host.strip())
                # final output formated for influx
                self.result.append('\n' + influx_output)

    def find_keys(self, node, kv):
        """
        Find all occurrences of a key in nested dictionaries and lists
        --> https://stackoverflow.com/a/19871956
        """
        if isinstance(node, list):
            for i in node:
                for k in self.find_keys(i, kv):
                    yield k
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for k in self.find_keys(j, kv):
                    yield k

    def clean(self):
        """ Reset vars for loop poller """
        self.dictags = {}
        self.result = []
        self.alive = []


class Influx:
    def __init__(self):
        self.influxdb_client = InfluxDBClient(
            host=Infpyng.hostname,
            port=Infpyng.port,
            username=Infpyng.user,
            password=Infpyng.pwd,
            ssl=False,
            verify_ssl=False,
            timeout=30
        )

    def init_db(self):
        # disable log messages from urllib3 library
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        try:
            self.influxdb_client.get_list_database()
        except requests.exceptions.ConnectionError:
            return False
        else:
            databases = self.influxdb_client.get_list_database()

            if len(list(filter(lambda x: x['name'] == Infpyng.dbname, databases))) == 0:
                self.influxdb_client.create_database(Infpyng.dbname)  # Create if does not exist.
            else:
                self.influxdb_client.switch_database(Infpyng.dbname)  # Switch to if does exist.
                self.influxdb_client.create_retention_policy(  # Create etention
                    'one_year',  # name
                    '52w',  # duration
                    '1',  # replication
                    default=True,
                    shard_duration='4w'
                )

            return self.influxdb_client

    def write_data(self, points):
        self.influxdb_client.write_points(points, protocol='line')
        self.influxdb_client.close()

