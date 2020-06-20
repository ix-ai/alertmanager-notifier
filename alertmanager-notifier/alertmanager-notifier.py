#!/usr/bin/env python3
""" Web server that translates alertmanager alerts into telegram messages """

import logging
import os
from waitress import serve
import telegram
from flask import Flask
from flask import request
from .lib import constants
from .lib import notifiers

a = Flask(__name__, template_folder='../templates')
a.secret_key = os.urandom(64).hex()

log = logging.getLogger(__package__)
version = f'{constants.VERSION}-{constants.BUILD}'


@a.route('/alert', methods=['POST'])
def parse_request():
    """ Converts the alert from alertmanager into HTML for telegram """
    content = request.get_json()

    return_message = ""
    try:
        log.info(f"Received {len(content['alerts'])} alert(s).")
        log.debug(f'Parsing content: {content}')
        return_message = n.notify(**content)
    except (KeyError, TypeError):
        message = 'Make sure that `Content-Type: application/json` is set and that the key `alerts` exists.'
        log.error(message)
        return_message = (message, 400)

    return return_message


@a.route('/healthz')
def healthz():
    """ Healthcheck """
    return (f'{__package__} {version}', 200)


def startup():
    """ Starts everything up """
    settings = {
        'telegram_token': os.environ.get('TELEGRAM_TOKEN'),
        'telegram_chat_id': os.environ.get('TELEGRAM_CHAT_ID'),
        'gotify_url': os.environ.get('GOTIFY_URL'),
        'gotify_token': os.environ.get('GOTIFY_TOKEN'),
        'port': int(os.environ.get('PORT', '8899')),
        'host': os.environ.get('ADDRESS', '*'),
        'telegram_template': os.environ.get('TELEGRAM_TEMPLATE', 'html.j2'),
        'telegram_template_too_long': os.environ.get('TELEGRAM_TEMPLATE_TOO_LONG', 'too_long.html.j2'),
        'gotify_template': os.environ.get('GOTIFY_TEMPLATE', 'markdown.md.j2'),
        'null_template': os.environ.get('NULL_TEMPLATE', 'text.j2'),
        'exclude_labels': os.environ.get('EXCLUDE_LABELS'),
        'notifiers': [],
    }

    if settings['telegram_token'] and settings['telegram_chat_id']:
        settings['notifiers'].append('telegram')
    if settings['gotify_url'] and settings['gotify_token']:
        settings['notifiers'].append('gotify')
    log.info(f"Starting {__package__} {version}, listening on {settings['host']}:{settings['port']}")
    return settings


if __name__ == '__main__':
    options = startup()
    try:
        if not options['notifiers']:
            log.warning('No notifier configured. Using `null`')
        n = notifiers.start(**options)
    except (ValueError, telegram.error.InvalidToken) as error:
        log.error(error)
    else:
        serve(a, host=options['host'], port=options['port'], ident=f'{__package__} {version}')
