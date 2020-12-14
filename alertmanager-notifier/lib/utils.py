#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Various utilities """

import logging
from distutils.util import strtobool
from flask import render_template

log = logging.getLogger(__package__)


def redact(params: dict, settings: dict, message: str) -> str:
    """
        based on params and the values of settings, it replaces sensitive
        information in message with a redacted string
    """
    for param, setting in params.items():
        if setting.get('redact') and settings.get(param):
            message = str(message).replace(settings.get(param), 'xxxREDACTEDxxx')
    return message


def convert_type(param: str, target: str):
    """
        converts string param to type target
    """
    converted = param
    if target == "boolean":
        converted = bool(strtobool(param))
    if target == "integer":
        converted = int(param)
    return converted


def template_message(include_title=False, template='markdown.md.j2', exclude_labels=True, current_length=0, **kwargs):
    """
    Formats the alerts for markdown notifiers

    Use `include_title` to specify if the title should be included in the message.
    If it's set to `False`, a separate key `title` will be returned.

    @return: False if the message processing fails otherwise dict
    """
    processed = {'message': ''}
    alerts_count = len(kwargs['alerts'])
    title = f"{alerts_count} alert(s) received"
    if not include_title:
        processed.update({'title': f"{title}"})
        title = None
    processed['message'] = render_template(
        template,
        title=title,
        alerts=kwargs['alerts'],
        external_url=kwargs['external_url'],
        receiver=kwargs['receiver'],
        exclude_labels=exclude_labels,
        current_length=current_length,
    )
    for alert in kwargs['alerts']:
        if int(alert['annotations'].get('priority', -1)) > processed.get('priority', -1):
            processed['priority'] = int(alert['annotations']['priority'])
    return processed
