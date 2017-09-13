# -*- coding: utf-8 -*-
import os

from magnivore.App import App
from magnivore.Config import Config
from magnivore.Interface import Interface
from magnivore.Logger import Logger
from magnivore.RulesParser import RulesParser

from pytest import fixture, raises

import ujson


@fixture
def default_file(request):
    with open('rules.json', 'w') as f:
        f.write("""{}""")

    def teardown():
        os.remove('rules.json')
    request.addfinalizer(teardown)


@fixture
def other_file(request):
    with open('rules2.json', 'w') as f:
        f.write("""{}""")

    def teardown():
        os.remove('rules2.json')
    request.addfinalizer(teardown)


@fixture
def app(mocker):
    mocker.patch.object(Config, 'get')
    mocker.patch.object(Interface, 'donor')
    mocker.patch.object(Interface, 'receiver')
    mocker.patch.object(RulesParser, 'parse')
    mocker.patch.object(ujson, 'load')
    return App


def test_run(app, default_file):
    app.run()
    RulesParser.parse.assert_called_with(ujson.load('rules.json'))


def test_run_file(app, other_file):
    app.run('rules2.json')
    RulesParser.parse.assert_called_with(ujson.load('rules2.json'))


def test_run_file_not_found(app):
    with raises(FileNotFoundError):
        app.run('xyz.json')


def test_run_verbosity(app, default_file):
    app.run(verbosity=1)


def test_run_log(mocker, app, default_file):
    mocker.patch.object(Logger, 'log')
    app.run()
    Logger.log.assert_called_with('run-verbosity', 0)
