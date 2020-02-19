#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Gotify """

import logging
from urllib.parse import urljoin
import requests
from ..lib import constants
from ..lib import processor
from . import core

log = logging.getLogger(__package__)


def start(**kwargs):
    """ Returns an instance of GotifyNotifier """
    return GotifyNotifier(**kwargs)


class GotifyNotifier(core.Notifier):
    """ The GotifyNotifier class """

    def __init__(
            self,
            gotify_token=None,
            gotify_url=None,
            gotify_template='markdown.md.j2',
            exclude_labels=True
    ):
        self.token = gotify_token
        self.url = urljoin(gotify_url, f'/message')
        self.template = gotify_template
        self.exclude_labels = exclude_labels
        log.debug(f"Initialized with {gotify_url}")
        super().__init__()

    def send(self, processed_alerts):
        """
        sends the notification to gotify

        @return True on success otherwise False
        """

        success = True
        headers = {
            'X-Gotify-Key': self.token,
            'user-agent': f'{__package__} {constants.VERSION}-{constants.BUILD}',
        }
        extras = {
            'client::display': {
                'contentType': 'text/markdown',
            }
        }
        req_json = {
            'extras': extras,
        }
        resp = None
        try:
            if 'message' in processed_alerts:
                req_json.update({'message': processed_alerts['message']})
            if 'title' in processed_alerts:
                req_json.update({'title': processed_alerts['title']})

            resp = requests.post(self.url, json=req_json, headers=headers)
        except requests.exceptions.RequestException as e:
            # Print exception if reqeuest fails
            log.warning(f'Could not connect to the Gotify server. The error: {e}')
            success = False
        except Exception as error:
            log.error(f'Failed to send message! Exception: {error}')
            success = False

        # Print request result if server returns http error code
        if resp is not None:
            if resp.status_code is not requests.codes.ok:  # pylint: disable=no-member
                log.warning(f'Error sending message to Gotify: {bytes.decode(resp.content)}')
                success = False
            else:
                log.info("Sent message to gotify")

        return success

    def notify(self, **kwargs):
        """ parses the arguments, formats the message and dispatches it """
        log.debug('Sending message to gotify')
        alerts = kwargs['alerts']
        processed_alerts = processor.template_message(
            alerts=alerts,
            include_title=False,
            template=self.template,
            exclude_labels=self.exclude_labels,
        )
        return self.send(processed_alerts)
