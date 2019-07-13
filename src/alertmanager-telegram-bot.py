#!/usr/bin/env python3
""" Web server that translates alertmanager alerts into telegram messages """

import logging
import os
import sys
import html
import telegram
from flask import Flask
from flask import request
from waitress import serve

LOG = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SETTINGS = {
    'telegram_token': os.environ.get('TELEGRAM_TOKEN'),
    'telegram_chat_id': os.environ.get('TELEGRAM_CHAT_ID'),
}

APP = Flask(__name__)
APP.secret_key = os.urandom(64).hex()
BOT = telegram.Bot(token=SETTINGS['telegram_token'])


@APP.route('/alert', methods=['POST'])
def parse_alert():
    """ Converts the alert from alertmanager into HTML for telegram """

    content = request.get_json()

    if not content or not content.get('alerts'):
        raise TypeError('`alerts` does not exist.')

    message = '{} alert(s)\n'.format(len(content['alerts']))

    for alert in content['alerts']:
        LOG.debug("Parsing alert: {}".format(alert))
        message += '<b>{}</b>\n'.format(alert['status'])

        for label in alert['labels']:
            message += '<b>{}</b>: {}\n'.format(label, alert['labels'][label])
        for annotation in alert['annotations']:
            message += '<b>{}</b>: {}\n'.format(annotation, alert['annotations'][annotation])

        message += '<a href="{}">Generator URL</a>\n\n'.format(alert['generatorURL'])
        return _post_message(message, content)


def _post_message(message, content=None):
    """ Sends the message to telegram """
    try:
        BOT.sendMessage(
            chat_id=SETTINGS['telegram_chat_id'],
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        LOG.debug("Sent message: {}".format(message))

    except TimeoutError as error:
        LOG.warning('TimeoutError: {}'.format(error))
        # This should get alertmanager to retry
        return "504 error - Internal Server Exception - TimeoutError", 504

    except Exception as error:
        # Catch all the other exceptions so that alertmanager doesn't go into a loop
        LOG.error("Exception occured: {}".format(error))
        LOG.error(content)
        exception_content = html.escape('{}'.format(error))
        body_content = html.escape('{}'.format(content))
        BOT.sendMessage(
            chat_id=SETTINGS['telegram_chat_id'],
            text=(
                'Failed to send alert to Telegram!\n',
                'Exception: <pre>{}</pre>\n'.format(exception_content),
                'Content: <pre>{}</pre>'.format(body_content)
            ),
            parse_mode='HTML',
        )

    return ""


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '9119'))
    host = '*'
    LOG.info("Starting alertmanager-telegram-bot, listening on {}:{}".format(host, port))
    serve(APP, host=host, port=port)
