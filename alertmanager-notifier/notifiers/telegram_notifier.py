#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Telegram """

import logging
import time
import telegram
from ..lib import processor
from . import core

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of TelegramNotifier """
    return TelegramNotifier(**kwargs)


class TelegramNotifier(core.Notifier):
    """ The TelegramNotifier class """

    def __init__(
            self,
            telegram_chat_id=None,
            telegram_token=None,
            telegram_template='html.j2',
            exclude_labels=True
    ):
        self.chat_id = telegram_chat_id
        self.notifier = telegram.Bot(token=telegram_token)
        self.template = telegram_template
        self.exclude_labels = exclude_labels
        log.debug(f"Initialized")
        super().__init__()

    def send(self, processed_alerts):
        """
        sends the notification to telegram

        @return True on success otherwise False
        """
        retry = True
        success = True
        while retry is True:
            try:
                self.notifier.sendMessage(
                    chat_id=self.chat_id,
                    text=processed_alerts['message'],
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                )
                log.info("Sent message to telegram.")
                retry = False
            except (TimeoutError, telegram.error.TimedOut, telegram.error.RetryAfter) as error:
                try:
                    retry_after = 0.5 + int(error.retry_after)
                except AttributeError:
                    retry_after = 2
                log.warning(f'Exception caught - retrying in {retry_after}s: {error}')
                time.sleep(retry_after)
            except (telegram.error.Unauthorized) as error:
                log.error(f'{error} - check TELEGRAM_TOKEN - skipping retries.')
                # Fake message_sent and return
                retry = False
                success = False
            except (telegram.error.BadRequest) as error:
                exit_message = ''
                if str(error) == 'Chat not found':
                    exit_message = f'Check TELEGRAM_CHAT_ID - '
                exit_message = f'{exit_message}Skipping retries. The exception: {error}'
                log.error(exit_message)
                retry = False
                success = False
            except Exception as error:
                log.error(f'Failed to send message! Exception: {error}')
                retry = False
                success = False
        return success

    def notify(self, **kwargs):
        """ parses the arguments, formats the message and dispatches it """
        log.debug('Sending message to telegram')
        alerts = kwargs['alerts']
        processed_alerts = processor.template_message(
            alerts=alerts,
            include_title=True,
            template=self.template,
            exclude_labels=self.exclude_labels,
        )
        return self.send(processed_alerts)
