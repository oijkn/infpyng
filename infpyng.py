#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import multiprocessing
import os
import signal
import subprocess
import sys
import time
from concurrent import futures

import include.logger as log
from include.parser import Parser


def infpyng(targets):
    args = [
        'fping',
        '-q',
        '-c', str(p.count),
        '-i', str(p.interval),
        '-p', str(p.period),
        '-t', str(p.timeout),
        '-B', str(p.backoff),
        '-r', str(p.retry),
        '-O', str(p.tos),
    ]

    cmd = args + targets
    # print('cmd: %s' % cmd)

    run = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)

    (output, errors) = run.communicate()
    lines = output.decode('utf-8').strip()

    return lines


def set_output(r, t):
    # parse output from fping to influxdb
    p.inf_parse(r, t)


def kill_childs():
    cmd = ['pgrep', '-f', 'infpyng']
    run = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE)

    (output, errors) = run.communicate()
    result = output.decode('utf-8').split()
    # debug('result =', result)
    for i in result:
        # debug('PID = ', i)
        if i != result[0]:
            os.kill(int(i), signal.SIGTERM)
            os.kill(int(i), signal.SIGINT)


def main():
    p.set_conf()
    # set all hosts to ping
    ips = p.set_targets()
    log.info(f'Targets to ping: {len(ips)}')
    # get numbers of CPUs
    cpu = multiprocessing.cpu_count() * 10
    log.info(f'Multiprocessing: {cpu}')
    # set buckets (number of ips / number of CPUs)
    buckets = round(len(ips) / cpu)
    if buckets == 0:
        buckets = cpu
    log.info(f'Buckets: {buckets}')
    # split list into other sublists
    chunks = [ips[x:x + buckets] for x in range(0, len(ips), buckets)]
    # start timer perf
    t_1 = time.perf_counter()
    # pool of threads and schedule the execution of tasks
    with futures.ProcessPoolExecutor(max_workers=cpu) as executor:
        futs = [
            (host, executor.submit(functools.partial(infpyng, host)))
            for host in chunks
        ]
    # to kill child without waiting
    executor.shutdown(wait=False)

    # get the result
    for ip, f in futs:
        # set timestamp for data point in nanosecond-precision Unix time
        timestamp = str(int(time.time() * 1000000000))
        if f.result():
            # print(f"result: {f.result()} for {ip}")
            set_output(f.result(), timestamp)

    # print final result for influxdb
    result = ''.join(p.result)
    log.info(f'Targets alive: {len(p.result)}')
    print(result)

    # end timer perf
    t_2 = time.perf_counter()
    log.info('Finished in: {:.2f} seconds'.format(round(t_2 - t_1, 2)))


if __name__ == "__main__":
    try:
        # init Class Parser
        p = Parser()
        # init logging
        log.set_logger(p.logfile)
        log.info('Settings loaded successfully')
        # start Infpyng
        log.info('Starting Infpyng multiprocessing')
        main()
    except KeyboardInterrupt:
        log.warning('Interrupted requested...exiting')
        kill_childs()
        try:
            sys.exit(0)
        finally:
            log.logging.shutdown()

