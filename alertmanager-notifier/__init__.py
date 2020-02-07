#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" initializes alertmanager_notifier """

import os
from .lib import log as logging

log = logging.setup_logger(
    name=__package__,
    level=os.environ.get('LOGLEVEL', 'INFO'),
)
