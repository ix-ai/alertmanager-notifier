#!/usr/bin/env python3
""" Web server that translates alertmanager alerts into telegram messages """

import html
import logging
import os
import sys
import time
from waitress import serve
import pygelf
import telegram
from flask import Flask
from flask import render_template
from flask import request
from .lib import constants

log = logging.getLogger(__package__)

app = Flask(__name__, template_folder='/templates')
app.secret_key = os.urandom(64).hex()


@app.route('/alert', methods=['POST'])
def parse_alert():
    """ Converts the alert from alertmanager into HTML for telegram """

    content = request.get_json()

    return_message = ""
    try:
        log.info('Received {} alert(s).'.format(len(content['alerts'])))
        log.debug("Parsing content: {}".format(content))
        return_message = __post_message(render_template(settings['template'], a=content), content)
    except TypeError:
        message = 'Make sure that `Content-Type: application/json` is set and that the key `alerts` exists.'
        log.error(message)
        return_message = (message, 400)

    return return_message


def __post_message(message, content=None):
    """ Sends the message to telegram """
    return_message = ""
    message_sent = False
    while message_sent is False:
        try:
            bot.sendMessage(
                chat_id=settings['telegram_chat_id'],
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            message_sent = True
            log.info("Sent message to telegram.")
            log.debug("Message: {}".format(message))
        except (TimeoutError, telegram.error.TimedOut, telegram.error.RetryAfter) as error:
            try:
                retry_after = 0.5 + int(error.retry_after)
            except AttributeError:
                retry_after = 2
            log.warning('Exception caught - retrying in {}s: {}'.format(retry_after, error))
            time.sleep(retry_after)
        except (telegram.error.Unauthorized) as error:
            exit_message = '{} - check TELEGRAM_TOKEN - skipping retries.'.format(error)
            log.error(exit_message)
            # Fake message_sent and return
            message_sent = True
            return_message = ('{}'.format(exit_message), 503)
        except (telegram.error.BadRequest) as error:
            exit_message = str(error)
            if str(error) == 'Chat not found':
                exit_message = '{} - check TELEGRAM_CHAT_ID'.format(exit_message)
            exit_message = '{} - skipping retries.'.format(exit_message)
            log.error(exit_message)
            # Fake message_sent and return
            message_sent = True
            return_message = ('{}'.format(exit_message), 503)
        except Exception as error:
            # Catch all the other exceptions so that alertmanager doesn't go into a loop
            log.error("Exception occured: {}".format(error))
            exception_content = html.escape('{}'.format(error))
            body_content = html.escape('{}'.format(content))
            text = 'Failed to send alert to Telegram!\n'
            text += 'Exception: <pre>{}</pre>\n'.format(exception_content)
            text += 'Content: <pre>{}</pre>'.format(body_content)
            bot.sendMessage(
                chat_id=settings['telegram_chat_id'],
                text=text,
                parse_mode='HTML',
            )

    return return_message


def configure_logging():
    """ Configures the logging """
    logging.basicConfig(
        stream=sys.stdout,
        level=settings['loglevel'],
        format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    if settings.get('gelf_host'):
        gelf = pygelf.GelfUdpHandler(
            name=__package__,
            level=settings['loglevel'],
            host=settings['gelf_host'],
            port=int(settings['gelf_port']),
            include_extra_fields=True,
            debug=True,
            _ix_id=os.path.splitext(sys.modules['__main__'].__file__)[0],
        )
        log.addHandler(gelf)
        log.info('Initialized logging with GELF enabled to {}:{}'.format)


if __name__ == '__main__':
    settings = {
        'telegram_token': os.environ.get('TELEGRAM_TOKEN'),
        'telegram_chat_id': os.environ.get('TELEGRAM_CHAT_ID'),
        'port': int(os.environ.get('PORT', '9119')),
        'host': os.environ.get('ADDRESS', '*'),
        'template': os.environ.get('TEMPLATE', 'notify.html.j2'),
        'gelf_host': os.environ.get('GELF_HOST'),
        'gelf_port': os.environ.get('GELF_PORT'),
        'loglevel': os.environ.get('LOGLEVEL', 'INFO'),
    }
    configure_logging()
    try:
        if not settings['telegram_token']:
            raise ValueError('TELEGRAM_TOKEN must be set!')
        if not settings['telegram_chat_id']:
            raise ValueError('TELEGRAM_CHAT_ID must be set!')
        bot = telegram.Bot(token=settings['telegram_token'])
    except (ValueError, telegram.error.InvalidToken) as error:
        log.error(error)
        sys.exit()

    log.warning("Starting {} {}-{}, listening on {}:{}".format(
        __package__,
        constants.VERSION,
        constants.BUILD,
        settings['host'],
        settings['port'],
    ))
    serve(app, host=settings['host'], port=settings['port'])
