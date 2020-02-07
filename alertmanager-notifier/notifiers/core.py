#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" notification core """

import logging
import importlib

log = logging.getLogger(__package__)


class NotifiersCore():
    """ the notification core class """

    notifiers = [
        'telegram',
        'gotify',
        'null',
    ]

    registered = []

    def __init__(self, **kwargs):
        """
        initializes the class

        it looks for `notifiers` (list) in the arguments, then iterates over all the
        arguments and uses all the other keys which (start with the same name) as
        arguments to initialize and register the notifier

        if no notifier is present, the `null` notifier will be used

        stores the notifiers in self.registered
        """
        notifiers = kwargs.get('notifiers', [])
        if not len(notifiers) > 0:
            notifiers = ['null']
        for notifier in notifiers:
            notifier_settings = {}
            for k, v in kwargs.items():
                # Ensures that only the settings for this notifier are passed
                if k.split('_')[0] == notifier:
                    notifier_settings.update({k: v})
            notifier_settings.update({'exclude_labels': kwargs.get('exclude_labels')})
            self.register(notifier, **notifier_settings)

    def register(self, notifier, **kwargs):
        """ registers a notifier """
        log.debug(f'Registering {notifier}')
        for n in self.notifiers:
            if n == notifier:
                instance = importlib.import_module(f'alertmanager-notifier.notifiers.{notifier}')
                self.registered.append({notifier: instance.Notifier(**kwargs)})
                log.debug(f'Registered {notifier}')

    def notify(self, **kwargs):
        """ dispatches a notification to the registered notifiers """
        return_message = ('All notification channels failed', 500)
        for notifiers in self.registered:
            for notifier in notifiers:
                log.debug(f'Sending notification to {notifier}')
                if notifiers[notifier].notify(**kwargs) is True:
                    return_message = 'OK'
        return return_message
