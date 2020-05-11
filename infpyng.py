#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import sys, os, subprocess, time
from parser import Parser

def main(targets):

    args = [
        '/usr/sbin/fping',
        '-q',
        '-c', str(p.count),
        '-i', str(p.interval),
        '-t', str(p.timeout),
        '-B', str(p.backoff),
        '-r', str(p.retry),
        '-O', str(p.tos),
    ]

    cmd = args + targets
    #print('cmd: %s' % cmd)

    r = subprocess.run(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    output = r.stdout.decode("utf-8").strip()

    # set timestamp for data point in nanosecond-precision Unix time
    timestamp = str(int(time.time() * 1000000000))

    # infParse output from fping for influx
    p.infParse(output, timestamp)

    sys.exit(0)

if __name__ == "__main__":
    # init Class Parser
    p = Parser()
    p.setConf()
    # call main function with all targets
    main(p.setTargets())
