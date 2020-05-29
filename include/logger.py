# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import sys


def init_logger(logfile):
    # disable log messages from polling2 library
    logging.getLogger('polling2').setLevel(logging.WARNING)

    logger = logging.getLogger()
    handler = logging.FileHandler(logfile)
    formatter = logging.Formatter(
        '%(asctime)-s %(name)-4s %(levelname)-4s %(message)s',
        '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def debug(msg):
    logger = logging.getLogger()
    logger.debug(msg)


def info(msg):
    logger = logging.getLogger()
    logger.info(msg)


def warning(msg):
    logger = logging.getLogger()
    logger.warning(msg)


def error(msg):
    logger = logging.getLogger()
    logger.error(msg)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def error(msg):
    logger = logging.getLogger()
    logger.error(msg)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

