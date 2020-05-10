#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import sys, os, subprocess, time
import reader, parser


def main(targets):

    args = [
        '/usr/sbin/fping',
        '-q',
        '-c', str(reader.count),
        '-i', str(reader.interval),
        '-t', str(reader.timeout),
        '-B', str(reader.backoff),
        '-r', str(reader.retry),
        '-O', str(reader.tos),
    ]

    cmd = args + targets
    #print('cmd: %s' % cmd)

    p = subprocess.run(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    output = p.stdout.decode("utf-8").strip()

    # set timestamp for data point in nanosecond-precision Unix time
    timestamp = str(int(time.time() * 1000000000))

    parser.parse(output, timestamp)

    sys.exit(0)

if __name__ == "__main__":
    reader.loadConfig()
    targets = reader.loadTargets()
    main(targets)
