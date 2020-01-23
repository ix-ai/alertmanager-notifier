#!/usr/bin/env python3
""" Web server that translates alertmanager alerts into telegram messages """

import logging
import os
import sys
import html
import telegram
import pause
import pygelf
from flask import Flask
from flask import render_template
from flask import request
from waitress import serve
import constants

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
    'template': os.environ.get('TEMPLATE', default='notify.html.j2'),
}

APP = Flask(__name__, template_folder='/templates')
APP.secret_key = os.urandom(64).hex()
BOT = telegram.Bot(token=SETTINGS['telegram_token'])


def configure_logging():
    """ Configures the logging """
    gelf_enabled = False

    if os.environ.get('GELF_HOST'):
        GELF = pygelf.GelfUdpHandler(
            host=os.environ.get('GELF_HOST'),
            port=int(os.environ.get('GELF_PORT', 12201)),
            debug=True,
            include_extra_fields=True,
            _ix_id=os.path.splitext(sys.modules['__main__'].__file__)[0][1:],  # sets it to `alertmanager-telegram-bot`
        )
        LOG.addHandler(GELF)
        gelf_enabled = True
    LOG.info('Initialized logging with GELF enabled: {}'.format(gelf_enabled))


@APP.route('/alert', methods=['POST'])
def parse_alert():
    """ Converts the alert from alertmanager into HTML for telegram """

    content = request.get_json()

    if not content or not content.get('alerts'):
        raise TypeError('`alerts` does not exist.')

    LOG.info('Received {} alert(s).'.format(len(content['alerts'])))
    LOG.debug("Parsing content: {}".format(content))

    message = render_template(SETTINGS['template'], a=content)

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
        LOG.info("Sent message to telegram.")
        LOG.debug("Message: {}".format(message))

    except (TimeoutError, telegram.error.TimedOut, telegram.error.RetryAfter) as error:
        LOG.warning('Exception caught - retrying: {}'.format(error))
        # Wait for 2 seconds and then return the error to alertmanager
        pause.seconds(2)
        return "504 error - Internal Server Exception - {}".format(error), 504

    except Exception as error:
        # Catch all the other exceptions so that alertmanager doesn't go into a loop
        LOG.error("Exception occured: {}".format(error))
        exception_content = html.escape('{}'.format(error))
        body_content = html.escape('{}'.format(content))
        text = 'Failed to send alert to Telegram!\n'
        text += 'Exception: <pre>{}</pre>\n'.format(exception_content)
        text += 'Content: <pre>{}</pre>'.format(body_content)
        BOT.sendMessage(
            chat_id=SETTINGS['telegram_chat_id'],
            text=text,
            parse_mode='HTML',
        )

    return ""


if __name__ == '__main__':
    configure_logging()
    port = int(os.environ.get('PORT', '9119'))
    host = os.environ.get('ADDRESS', '*')
    # pylint: disable=no-member
    LOG.info("Starting alertmanager-telegram-bot {}, listening on {}:{}".format(constants.VERSION, host, port))
    LOG.info("Using templates/{} for message templating".format(SETTINGS['template']))
    serve(APP, host=host, port=port)
