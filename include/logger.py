# -*- coding: utf-8 -*-

import logging
import sys

from include.core import Infpyng


def set_logger():
    # init Class Infpyng
    core = Infpyng()

    # disable log messages from polling2 library
    logging.getLogger('polling2').setLevel(logging.WARNING)

    logger = logging.getLogger()
    handler = logging.FileHandler(core.logfile)
    formatter = logging.Formatter(
        '%(asctime)-s %(name)-4s %(levelname)-4s %(message)s',
        '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    if core.set_logger() is None:
        warning(':: No config file found...exiting')
        sys.exit()

    return core


def debug(msg):
    logger = logging.getLogger()
    logger.debug(msg)


def info(msg):
    logger = logging.getLogger()
    logger.info(msg)


def warning(msg):
    logger = logging.getLogger()
    logger.warning(msg)

