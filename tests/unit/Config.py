# -*- coding: utf-8 -*-
from magnivore.Config import Config


def test_defaults():
    result = Config.default
    assert result['donor']['name'] == 'donor.db'
    assert result['donor']['type'] == 'sqlite'
    assert result['donor']['auth']['user'] == ''
    assert result['donor']['auth']['password'] == ''
    assert result['donor']['auth']['host'] == ''
    assert result['receiver']['name'] == 'receiver.db'
    assert result['receiver']['type'] == 'sqlite'
    assert result['receiver']['auth'] == result['donor']['auth']
