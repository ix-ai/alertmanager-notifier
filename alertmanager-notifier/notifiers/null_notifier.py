#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Gotify """

import logging
from . import core

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of NullNotifier """
    return NullNotifier(**kwargs)


class NullNotifier(core.Notifier):  # pylint: disable=too-few-public-methods
    """ The NullNotifier class """

    def __init__(self, null_template='text.j2', exclude_labels=True):
        self.template = null_template
        self.exclude_labels = exclude_labels
        log.debug(f"Initialized")
        super().__init__()
