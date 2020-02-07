#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Initializes the notifier core """

from . import core


def start(**kwargs):
    """ Returns an instance of NotifiersCore() """
    return core.NotifiersCore(**kwargs)
