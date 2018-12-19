# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.module_loading import import_string


def load_backend(path):
    return import_string(path)()


def send_sms(*args, **kwargs):
    backend = load_backend(settings.SEND_SMS_BACKEND)
    return backend.send_sms(*args, **kwargs)
