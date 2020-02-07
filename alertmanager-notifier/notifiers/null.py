#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Gotify """

import logging
from ..lib import processor

log = logging.getLogger(__package__)


class Notifier():
    """ The notify class """

    def __init__(self, null_template='text.j2', exclude_labels=True):
        self.template = null_template
        self.exclude_labels = exclude_labels
        log.debug(f"Initialized")

    def send(self, processed_alerts):
        """
        logs the notification to info

        @return True
        """
        log.info(f"\n{processed_alerts['message'].replace('#','')}")
        return True

    def notify(self, **kwargs):
        """ parses the arguments, formats the message and dispatches it """
        log.debug('Sending message to null')
        alerts = kwargs['alerts']
        processed_alerts = processor.template_message(
            alerts=alerts,
            include_title=True,
            template=self.template,
            exclude_labels=self.exclude_labels,
        )
        return self.send(processed_alerts)

    def noop(self):
        """ Does nothing except keeping pylint happy"""
