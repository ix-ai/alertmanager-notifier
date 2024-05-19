#!/usr/bin/env python3
""" Web server that translates alertmanager alerts into messages for other services """

import logging
import os
from waitress import serve
import telegram
from flask import Flask
from flask import request
from .lib import constants
from .lib import notifiers
from .lib.utils import redact
from .lib.utils import convert_type

a = Flask(__name__, template_folder='../templates')
a.secret_key = os.urandom(64).hex()

log = logging.getLogger(__package__)
version = f'{constants.VERSION}-{constants.BUILD}'


@a.route('/alert', methods=['POST'])
def parse_request():
    """ Receives the alert and sends the notification """
    content = request.get_json()

    return_message = ""
    try:
        log.info(f"Received {len(content['alerts'])} alert(s).")
        log.debug(f'Parsing content: {content}')
        # pylint: disable-next=possibly-used-before-assignment
        return_message = n.notify(**content)
    except (KeyError, TypeError) as e:
        message = (
            'Make sure that `Content-Type: application/json` is set and that the key `alerts` exists.'
            f'The exception: {e}'
        )
        log.error(message)
        return_message = (message, 400)

    return return_message


@a.route('/healthz')
def healthz():
    """ Healthcheck """
    return (f'{__package__} {version}', 200)


def startup():
    """ Starts everything up """
    params = {
        'telegram_token': {
            'type': 'string',
            'redact': True,
        },
        'telegram_chat_id': {
            'type': 'string',
        },
        'telegram_always_succeed': {
            'type': 'boolean',
            'default': 'no',
        },
        'telegram_max_retries': {
            'type': 'integer',
            'default': '0',
        },
        'gotify_url': {
            'type': 'string',
        },
        'gotify_token': {
            'type': 'string',
            'redact': True,
        },
        'port': {
            'type': 'integer',
            'default': '8899',
        },
        'address': {
            'type': 'string',
            'default': '*',
        },
        'telegram_template': {
            'type': 'string',
            'default': 'html.j2',
        },
        'telegram_template_too_long': {
            'type': 'string',
            'default': 'too_long.html.j2',
        },
        'gotify_template': {
            'type': 'string',
            'default': 'markdown.md.j2',
        },
        'null_template': {
            'type': 'string',
            'default': 'text.j2',
        },
        'exclude_labels': {
            'type': 'boolean',
            'default': 'yes',
        }
    }

    settings = {
        'notifiers': [],
    }

    for param, param_settings in params.items():
        try:
            settings.update({param: convert_type(os.environ[param.upper()], param_settings['type'])})
        except ValueError:  # Wrong value for the environment variable
            log.warning(f"`{os.environ[param.upper()]}` not understood for {param.upper()}. Ignoring.")
        except KeyError:  # No environment variable set for the param
            pass

        try:
            if param not in settings:
                settings[param] = convert_type(param_settings['default'], param_settings['type'])
            log.info(f'{param.upper()} is set to `{redact(params, settings, settings[param])}`')
        except KeyError:  # No default value for the param
            pass

    try:
        if settings['telegram_token'] and settings['telegram_chat_id']:
            settings['notifiers'].append('telegram')
    except KeyError:
        pass

    try:
        if settings['gotify_url'] and settings['gotify_token']:
            settings['notifiers'].append('gotify')
    except KeyError:
        pass

    log.info(f"Starting {__package__} {version}, listening on {settings['address']}:{settings['port']}")
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
        serve(a, host=options['address'], port=options['port'], ident=f'{__package__} {version}')
