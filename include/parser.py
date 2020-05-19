# -*- coding: utf-8 -*-

import glob
import operator
import os
import socket
import sys
from functools import reduce

import toml


def find_keys(node, kv):
    """
    Find all occurrences of a key in nested dictionaries and lists
    --> https://stackoverflow.com/a/19871956
    """
    if isinstance(node, list):
        for i in node:
            for k in find_keys(i, kv):
                yield k
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for k in find_keys(j, kv):
                yield k


class Parser:
    def __init__(self):
        # set path where script is running
        self.path = os.path.realpath(
            os.path.join(os.getcwd(),
                         os.path.dirname(__file__))
        )
        # set globs of all TOML files
        self.globs = glob.glob(os.path.dirname(self.path) + "/config/*.toml")
        # set global vars
        self.count = int(1)
        self.interval = int(10)
        self.period = int(1000)
        self.timeout = int(500)
        self.backoff = float(1.5)
        self.retry = int(3)
        self.tos = int(0)
        # dict with all host -> tags
        self.dictags = {}
        # list for final result
        self.result = []
        # default log file
        self.logfile = '/var/log/infpyng.log'

    def set_conf(self):
        """
        Loads infpyng configuration from a TOML file.
        """
        if any("config.toml" in f for f in self.globs):
            config = toml.load(os.path.dirname(self.path) + "/config/config.toml")
            if 'count' in config['options']:
                self.count = int(config['options']['count'])
            if 'interval' in config['options']:
                self.interval = int(config['options']['interval'])
            if 'period' in config['options']:
                self.period = int(config['options']['period'])
            if 'timeout' in config['options']:
                self.timeout = int(config['options']['timeout'])
            if 'backoff' in config['options']:
                self.backoff = float(config['options']['backoff'])
            if 'retry' in config['options']:
                self.retry = int(config['options']['retry'])
            if 'tos' in config['options']:
                self.tos = int(config['options']['tos'])
            if 'path' in config['logging']:
                self.logfile = str(config['logging']['path'])

            # loads targets from a TOML file(s)
            Parser.set_targets(self)
        else:
            # TODO: return false to log file
            print('Error: no config file found !')
            sys.exit(1)

    def set_targets(self):
        """
        Loads targets from a TOML file(s) and prepare dict with
        all tags if they are set.
        """
        # exclude config file from glob
        toml_files = [x for x in self.globs if "config.toml" not in x]

        # set list for all targets
        all_targets = []
        # loop in all file to find value(s) of 'hosts' keys
        for toml_file in toml_files:
            targets = toml.load(toml_file)
            list2d = find_keys(targets, 'hosts')
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

                # final output formated for influx
                self.result.append('\n' + influx_output)

