# coding: utf-8

from dext.common.utils.app_settings import app_settings

xsolla_settings = app_settings('XSOLLA',
                               SECRET_KEY='secret_key',
                               ALLOWED_IPS=('127.0.0.1', 'testserver', 'localhost'))
