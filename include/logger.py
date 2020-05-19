# -*- coding: utf-8 -*-

import logging


def set_logger(file):
    logger = logging.getLogger()
    handler = logging.FileHandler(file)
    formatter = logging.Formatter(
        '%(asctime)-s     %(name)-8s %(levelname)-8s %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
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

