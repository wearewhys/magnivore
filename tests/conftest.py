# -*- coding: utf-8 -*-
import os
from unittest.mock import MagicMock

from magnivore.Config import Config
from magnivore.Interface import Interface
from magnivore.Tracker import Tracker
from magnivore.Transformer import Transformer

from pytest import fixture


@fixture
def config_teardown(request):
    """
    Removes the testing configuration file
    """
    def teardown():
        os.remove('magnivore-test.json')
    request.addfinalizer(teardown)


@fixture
def config():
    """
    A basic config dictionary to replace the real one
    """
    config = {
        'donor': {
            'name': 'donor.db',
            'type': 'sqlite',
            'auth': {
                'user': 'donor'
            }
        },
        'receiver': {
            'name': 'receiver.db',
            'type': 'sqlite',
            'auth': {
                'user': 'receiver'
            }
        }
    }
    return config


@fixture
def logger():
    """
    Mock the logger
    """
    return MagicMock()


@fixture
def parser_dependencies(mocker):
    """
    Mocks all the parser dependencies so that no IO calls are made
    """
    mocker.patch.object(Interface, 'donor')
    mocker.patch.object(Interface, 'receiver')
    mocker.patch.object(Config, 'get')
    mocker.patch.object(Transformer, 'transform')
    mocker.patch.object(Tracker, 'track')
