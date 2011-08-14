# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Configuration settings.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE for more details.
"""
config = {}

# Configurations for the 'tipfy' module.
config['tipfy'] = {
    # Enable debugger. It will be loaded only in development.
    'middleware': [
        'tipfy.ext.debugger.DebuggerMiddleware',
        'tipfy.ext.appstats.AppstatsMiddleware',
    ],
    # Enable the Hello, World! app example.
    'apps_installed': [
        'apps.base',
        'apps.auth',
        'apps.account',
        'apps.kid',
    ],
}

config['tipfy.ext.session'] = {
    'secret_key': 'W%d/[|(JM}c6@9#@ymNtu!7ZGnOZ95!DlNS!^.t`1SU%G"%{ty',
}

config['tipfy.ext.auth.facebook'] = {
    'api_key':    '163ae0a68ac6c5e0166b12f948d48ea7',
    'app_secret': 'e7b1118c1d8d1ced3f76f143c717c240',
}

config['tipfy.ext.auth.friendfeed'] = {
    'consumer_key':    'XXXXXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXXXXX',
}

config['tipfy.ext.auth.twitter'] = {
    'consumer_key':    'tWC9pjCSb27ZxNRlIyuVw',
    'consumer_secret': '1TRcwzBZC7rWqAP4AreiNzmrdOX22SpwEMWAL5NuU',
}

