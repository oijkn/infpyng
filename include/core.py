# -*- coding: utf-8 -*-

import glob
import operator
import os
import sys
import socket
import logging
import requests
import datetime
import time
from influxdb import InfluxDBClient
from functools import reduce

import toml

import include.logger as log


class Infpyng:
    # set version of script
    version = ''
    # set conf.toml file
    config = {}
    # set options
    poll = int(60)
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

    def __init__(self):
        # set path where script is running
        self.path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # set defaut log file
        self.logfile = os.path.dirname(self.path) + "/infpyng.log"
        # gracefully quit ProcessPoolExecutor
        self.bye = True

    def init_infpyng(self):
        self.set_logger()
        self.set_conf()
        self.set_targets()

    def set_conf(self):
        """ Loads infpyng configuration from a TOML file """
        self.config = toml.load(
            os.path.dirname(self.path) + "/config/config.toml")
        options = self.config['options']
        if 'poll' in options:
            self.poll = int(options['poll'])
            if self.poll < 60:
                self.poll = 60
        if 'count' in options:
            self.count = int(options['count'])
            if self.count < 1:
                self.count = 1
        if 'interval' in options:
            self.interval = int(options['interval'])
            if self.interval < 1:
                self.interval = 1
        if 'period' in options:
            self.period = int(options['period'])
            if self.period < 10:
                self.period = 10
        if 'timeout' in options:
            self.timeout = int(options['timeout'])
            if self.timeout < self.period:
                self.timeout = self.period
        if 'backoff' in options:
            self.backoff = float(options['backoff'])
        if 'retry' in options:
            self.retry = int(options['retry'])
        if 'tos' in options:
            self.tos = int(options['tos'])
        self.version = self.config['config']['version']

    def set_logger(self):
        # set globs of all TOML files
        globs = glob.glob(os.path.dirname(self.path) + "/config/*.toml")
        if any("config.toml" in f for f in globs):
            self.config = toml.load(
                os.path.dirname(self.path) + "/config/config.toml")
            logs = self.config['logging']
            if 'path' in logs:
                self.logfile = str(logs['path'])
            # create file if it's not exist
            file_exists = os.path.isfile(self.logfile)
            if not file_exists:
                with open(self.logfile, 'a'): pass
            os.chmod(self.logfile, 0o644)
            # init logging
            log.init_logger(self.logfile)
        else:
            log.error(':: No config file found...exiting')
            log.eprint(':: Infpyng :: No config file found...exiting')
            sys.exit()

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
                    tags = ',' + ','.join(f'{key}={value}'
                                          for key, value in item)
                else:
                    tags = ''

                # prepare output for influxdb
                influx_output = (
                    'infpyng,host=' + socket.gethostname() +
                    ',target=' + host.strip() +
                    tags +
                    ' average_response_ms=' + avg +
                    ',maximum_response_ms=' + max_ +
                    ',minimum_response_ms=' + min_ +
                    ',packets_received=' + recv + 'i' +
                    ',packets_transmitted=' + sent + 'i' +
                    ',percent_packet_loss=' + loss.strip('%') + ' ' +
                    timestamp)
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

    def round_time(self,
                   dt=None,
                   date_delta=datetime.timedelta(minutes=1),
                   to='average'):
        """
        Round a datetime object to a multiple of a timedelta
        dt : datetime.datetime object, default now.
        dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
        -->  https://stackoverflow.com/a/32547090
        """
        round_to = date_delta.total_seconds()
        if dt is None:
            dt = datetime.datetime.now()
        seconds = (dt - dt.min).seconds

        if seconds % round_to == 0 and dt.microsecond == 0:
            rounding = (seconds + round_to / 2) // round_to * round_to
        else:
            if to == 'up':
                # // is a floor division, not a comment on following line (like in javascript):
                rounding = (seconds + dt.microsecond / 1000000 +
                            round_to) // round_to * round_to
            elif to == 'down':
                rounding = seconds // round_to * round_to
            else:
                rounding = (seconds + round_to / 2) // round_to * round_to

        return dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)

    def clean(self):
        """ Reset vars for loop poller """
        self.dictags = {}
        self.result = []
        self.alive = []


class Influx:
    # set InfluxDB
    hostname = str('localhost')
    port = int(8086)
    dbname = str('infpyng')
    user = ''
    pwd = ''
    retention_name = 'one_year'
    retention_duration = '52w'
    replication = int(1)
    shard_duration = '4w'

    def __init__(self):
        # set path where script is running
        self.path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.config = toml.load(
            os.path.dirname(self.path) + "/config/config.toml")
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
        if 'retention_name' in influx:
            self.retention_name = str(influx['retention_name'])
        if 'retention_duration' in influx:
            self.retention_duration = str(influx['retention_duration'])
        if 'replication' in influx:
            self.replication = int(influx['replication'])
        if 'shard_duration' in influx:
            self.shard_duration = str(influx['shard_duration'])
        # configure connexion to InfluxDB
        self.influxdb_client = InfluxDBClient(
            host=self.hostname,
            port=self.port,
            username=self.user,
            password=self.pwd,
            ssl=False,
            verify_ssl=False,
            timeout=30)

    def init_db(self):
        # disable log messages from urllib3 library
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        try:
            self.influxdb_client.get_list_database()
        except requests.exceptions.ConnectionError:
            return False
        else:
            databases = self.influxdb_client.get_list_database()

            if len(
                    list(
                        filter(lambda x: x['name'] == self.dbname,
                               databases))) == 0:
                self.influxdb_client.create_database(
                    self.dbname)  # Create if does not exist.

            self.influxdb_client.switch_database(
                self.dbname)  # Switch to if does exist.
            self.influxdb_client.create_retention_policy(  # Create retention
                self.retention_name,
                self.retention_duration,
                self.replication,
                default=True,
                shard_duration=self.shard_duration)

            return self.influxdb_client

    def write_data(self, points):
        try:
            self.influxdb_client.write_points(points, protocol='line')
            self.influxdb_client.close()
            return True
        except requests.exceptions.ConnectionError:
            log.error(':: Entry was not recorded, Influx connection error')
            log.eprint(':: Infpyng :: Entry was not recorded, Influx connection error')
            log.info(':: Sleep time to %s sec' % str(20))
            time.sleep(20)
            return False

