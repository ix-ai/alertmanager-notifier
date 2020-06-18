#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Formats the alertmanager alerts into messages """

import logging
from flask import render_template

log = logging.getLogger(__package__)


def template_message(alerts, include_title=False, template='markdown.md.j2', exclude_labels=True, current_length=0):
    """
    Formats the alerts for markdown notifiers

    Use `include_title` to specify if the title should be included in the message.
    If it's set to `False`, a separate key `title` will be returned.

    @return: False if the message processing fails otherwise dict
    """
    processed = {'message': ''}
    alerts_count = len(alerts)
    title = f"{alerts_count} alert(s) received"
    message = ''
    if not include_title:
        processed.update({'title': f"{title.replace('#','')}"})
        title = None
    message = render_template(
        template,
        title=title,
        alerts=alerts,
        exclude_labels=exclude_labels,
        current_length=current_length,
    )
    processed['message'] = message.replace('#', '')
    return processed
