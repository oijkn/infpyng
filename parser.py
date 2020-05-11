# -*- coding: utf-8 -*-

import sys, os, glob, toml, operator, socket
from functools import reduce

# For debug
from pprint import pprint

class Parser:
    def __init__(self):
        # set path where script is running
        self.path = os.path.realpath(
            os.path.join(os.getcwd(),
            os.path.dirname(__file__))
        )
        # set globs of all TOML files
        self.globs = glob.glob(self.path + "/config/*.toml")
        # set global vars
        self.count = int(1)
        self.interval = int(10)
        self.timeout = int(500)
        self.backoff = float(1.5)
        self.retry = int(3)
        self.tos = int(0)

    def loadConfig(self):
        """
        Loads infpyng configuration from a TOML file.
        """
        if any("config.toml" in f for f in self.globs):
            config = toml.load(self.path + '/config/config.toml')
            if 'count' in config['options']:
                self.count = int(config['options']['count'])
            if 'interval' in config['options']:
                self.interval = int(config['options']['interval'])
            if 'timeout' in config['options']:
                self.timeout = int(config['options']['timeout'])
            if 'backoff' in config['options']:
                self.backoff = float(config['options']['backoff'])
            if 'retry' in config['options']:
                self.retry = int(config['options']['retry'])
            if 'tos' in config['options']:
                self.tos = int(config['options']['tos'])

            # loads targets from a TOML file(s)
            Parser.loadTargets(self)

        else:
            print('Error: no config file found !')
            sys.exit(1)

    def loadTargets(self):
        """
        Loads targets from a TOML file(s).
        """
        # exclude config file from glob
        tomlFiles = [ x for x in self.globs if "config.toml" not in x ]

        # set list for all targets
        allTargets = []
        # loop in all file to find value(s) of 'hosts' keys
        for tomlFile in tomlFiles:
            targets = toml.load(tomlFile)
            list2d = Parser.findKeys(targets, 'hosts')
            allTargets = list(list2d) + allTargets
            #pprint(allTargets)

        # make flat list out of list of lists
        # --> https://stackoverflow.com/a/39493960
        allTargets = reduce(operator.concat, allTargets)

        return allTargets

    def loadTags(self, host):
        """
        Loads tags from a TOML file.
        """
        # exclude config file from glob
        tomlFiles = [ x for x in self.globs if "config.toml" not in x ]

        # parse targets and match keys 'tags' for wanted host
        # --> https://stackoverflow.com/q/61714213/6281137
        for tomlFile in tomlFiles:
            targets = toml.load(tomlFile)

            #pprint('host: %s' % host)
            #pprint('targets: %s' % targets['targets'])

            for target in targets['targets']:
                if host in target['hosts'] and 'tags' in target:
                    tags = ','.join("{!s}={!r}".format(key, val) for (key, val) in target['tags'].items())
                    tags = tags.replace("'", "")

                    return tags

            """ Alternative """
            """
            hosts = operator.itemgetter('hosts')
            tags = operator.itemgetter('tags')
            fmt = 'country={country},server={server}'
            space = targets['targets']

            term = host
            # filter
            items = (item for item in space if term in hosts(item))
            for item in items:
                #print(f'host:{term}')
                #print(fmt.format(**tags(item)))
            # or
                print(','.join(f'{key}={value}' for key,value in tags(item).items()))
            """

    def parse(self, data, timestamp):
        """
        Parse infpyng response from fping cmd.
        # '1.1.1.1 : xmt/rcv/%loss = 1/1/0%, min/avg/max = 1.35/1.35/1.35'
        # measurement_name,myhost=hostname1,mytag=server used=10.00 1589048898016737024
        """
        for line in data.splitlines():
            # get host and metrics
            [host, s1] = line.split(" : ")
            # host is alive
            if s1.find(',') != -1:
                [stats, ping] = s1.split(", ")
                # get packet loss %
                [_, s2] = stats.split(" = ")
                [sent, recv, loss] = s2.split("/")
                # get latency
                [_, s3] = ping.split(" = ")
                [min_, avg, max_] = s3.split("/")

                # if tags is set
                tags = Parser.loadTags(self, host.strip())
                if tags:
                    tags = ',' + tags
                else:
                    tags = ''

                # prepare output for influxdb
                influxOutput = ('infpyng,host=' + socket.gethostname() +
                                ',target=' + host.strip() +
                                tags +
                                ' average_response_ms=' + avg +
                                ',maximum_response_ms=' + max_ +
                                ',minimum_response_ms=' + min_ +
                                ',packets_received=' + recv + 'i' +
                                ',packets_transmitted=' + sent + 'i' +
                                ',percent_packet_loss=' + loss.strip('%') + 'i' +
                                ' ' + timestamp
                )

                # final output formated for influx
                print(influxOutput)

    def findKeys(node, kv):
        """
        Find all occurrences of a key in nested dictionaries and lists
        --> https://stackoverflow.com/a/19871956
        """
        if isinstance(node, list):
            for i in node:
                for x in Parser.findKeys(i, kv):
                   yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in Parser.findKeys(j, kv):
                    yield x
