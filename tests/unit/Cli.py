# -*- coding: utf-8 -*-
from click.testing import CliRunner

from magnivore.App import App
from magnivore.Cli import Cli
from magnivore.Config import Config
from magnivore.Tracker import Tracker, database

from pytest import fixture, mark


@fixture
def app_mock(mocker):
    mocker.patch.object(App, 'run')


@fixture
def runner():
    return CliRunner()


def test_cli_run(app_mock, runner):
    runner.invoke(Cli.run)
    App.run.assert_called_with()


def test_cli_run_rules(app_mock, runner):
    runner.invoke(Cli.run, ['magic.json'])
    App.run.assert_called_with(rules_file='magic.json')


@mark.parametrize('verbosity', ['-v', '--verbose'])
def test_cli_run_verbose(app_mock, runner, verbosity):
    runner.invoke(Cli.run, [verbosity])
    App.run.assert_called_with(verbosity=1)


def test_cli_init(mocker, runner):
    mocker.patch.object(database, 'create_tables')
    mocker.patch.object(database, 'commit')
    runner.invoke(Cli.init)
    database.create_tables.assert_called_with([Tracker])
    assert database.commit.call_count == 1


def test_cli_config_skeleton(mocker, runner):
    mocker.patch.object(Config, 'set_to_default')
    mocker.patch.object(Config, 'save')
    runner.invoke(Cli.config_skeleton)
    assert Config.set_to_default.call_count == 2
    assert Config.save.call_count == 1


def test_cli_hello(runner):
    result = runner.invoke(Cli.hello)
    assert result.output == '0.3.1\n'


def test_cli_version(runner):
    result = runner.invoke(Cli.version)
    assert result.output == '0.3.1\n'
