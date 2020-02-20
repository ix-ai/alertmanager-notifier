#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" notification core """

import logging
from ix_notifiers.core import IxNotifiers
from . import processor

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of Notify() """
    n = Notify()
    notifiers = kwargs.get('notifiers', [])
    if not len(notifiers) > 0:
        notifiers = ['null']
    for notifier in notifiers:
        notifier_settings = {}
        for k, v in kwargs.items():
            # Ensures that only the settings for this notifier are passed
            if k.split('_')[0] == notifier:
                notifier_settings.update({k: v})
        notifier_settings.update({'exclude_labels': kwargs.get('exclude_labels', True)})
        n.register(notifier, **notifier_settings)
    return Notify(**kwargs)


class Notify(IxNotifiers):
    """ the Notify class """

    def __init__(self, **kwargs):
        self.telegram_template = kwargs.get('telegram_template', 'html.j2')
        self.gotify_template = kwargs.get('gotify_template', 'markdown.md.j2')
        self.null_template = kwargs.get('null_template', 'text.j2')
        self.exclude_labels = kwargs.get('exclude_labels', True)
        super().__init__()

    def notify(self, **kwargs):
        """ dispatches a notification to the registered notifiers """
        success = ('All notification channels failed', 500)
        for notifier_name, notifier in self.registered.items():
            log.debug(f'Sending notification to {notifier_name}')
            notification_method = self.__getattribute__(f'{notifier_name}_notify')
            if notification_method(notifier=notifier, **kwargs):
                success = ('OK', 200)
        return success

    def gotify_notify(self, notifier, **kwargs):
        """ parses the arguments, formats the message and dispatches it """
        log.debug('Sending message to gotify')
        processed_alerts = processor.template_message(
            alerts=kwargs['alerts'],
            include_title=False,
            template=self.gotify_template,
            exclude_labels=self.exclude_labels,
        )
        return notifier.send(**processed_alerts)

    def telegram_notify(self, notifier, **kwargs):
        """ parses the arguments, formats the message and dispatches it """
        log.debug('Sending message to telegram')
        processed_alerts = processor.template_message(
            alerts=kwargs['alerts'],
            include_title=True,
            template=self.telegram_template,
            exclude_labels=self.exclude_labels,
        )
        processed_alerts.update({'parse_mode': 'HTML'})
        return notifier.send(**processed_alerts)

    def null_notify(self, notifier, **kwargs):
        """ dispatches directly """
        log.debug('Sending message to null')
        processed_alerts = processor.template_message(
            alerts=kwargs['alerts'],
            include_title=True,
            template=self.null_template,
            exclude_labels=self.exclude_labels,
        )
        return notifier.send(**processed_alerts)
