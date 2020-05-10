# -*- coding: utf-8 -*-

import socket
from reader import loadTags

# '1.1.1.1 : xmt/rcv/%loss = 1/1/0%, min/avg/max = 1.35/1.35/1.35'
# measurement_name,myhost=hostname1,mytag=server used=10.00 1589048898016737024

def parse(data, timestamp):
    """
    Parse infpyng response from fping cmd.
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
            if loadTags(host.strip()):
                tags = ',' + loadTags(host.strip())
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

            print(influxOutput)
