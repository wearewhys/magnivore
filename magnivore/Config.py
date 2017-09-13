# -*- coding: utf-8 -*-
from aratrum import Aratrum


class Config(Aratrum):
    """
    Wrapper for Aratrum. A 'magnivore.json' file is used instead.
    """
    auth = {
        'user': '',
        'password': '',
        'host': ''
    }

    default = {
        'donor': {
            'name': 'donor.db',
            'type': 'sqlite',
            'auth': auth
        },
        'receiver': {
            'name': 'receiver.db',
            'type': 'sqlite',
            'auth': auth
        }
    }
