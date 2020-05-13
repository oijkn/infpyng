#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import sys, multiprocessing, subprocess, time, functools
from concurrent import futures
from parser import Parser

def infpyng(targets):

    args = [
        'fping',
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

    r = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    (output, errors) = r.communicate()

    lines = output.decode('utf-8').strip()

    return lines

def setOutput(result, time):
    # parse output from fping to influxdb
    p.infParse(result, time)

if __name__ == "__main__":
    # init Class Parser
    p = Parser()
    p.setConf()
    # set all hosts to ping
    ips = p.setTargets()
    # get numbers of CPUs
    cpu = multiprocessing.cpu_count() * 10
    # set buckets (number of ips / number of CPUs)
    buckets = round(len(ips) / cpu)
    if buckets == 0:
        buckets = cpu
    # split list into other sublists
    chunks = [ips[x:x+buckets] for x in range(0, len(ips), buckets)]
    # pool of threads and schedule the execution of tasks
    with futures.ProcessPoolExecutor(max_workers=cpu) as executor:
        futs = [
            (host, executor.submit(functools.partial(infpyng, host)))
            for host in chunks
        ]
    # get the result
    for ip, f in futs:
        # set timestamp for data point in nanosecond-precision Unix time
        tm = str(int(time.time() * 1000000000))
        if f.result():
            #print(f"result: {f.result()} for {ip}")
            setOutput(f.result(), tm)

    result = ''.join(p.result)
    print(result)
