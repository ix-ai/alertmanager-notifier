#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Global logging configuration """

import logging


def setup_logger(name=__package__, level='INFO'):
    """ sets up the logger """
    logging.basicConfig(handlers=[logging.NullHandler()])
    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d %(levelname)s [%(module)s.%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
