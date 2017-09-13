# -*- coding: utf-8 -*-
import logging

from magnivore.Logger import Logger

from pytest import fixture, mark


@fixture
def logger_mock(mocker):
    mocker.patch.object(Logger, 'start_logger')
    mocker.patch.object(Logger, 'add_handler')


@fixture
def logger(mocker):
    mocker.patch.object(logging, 'getLogger')
    return Logger()


def test_init(logger_mock):
    logger = Logger()
    logger.start_logger.assert_called_with(50)
    logger.add_handler.assert_called_with(50, 'stdout')
    # then i'll decide on the default level


@mark.parametrize('verbosity, level', [
    (0, logging.CRITICAL),
    (1, logging.ERROR),
    (2, logging.WARNING),
    (3, logging.INFO),
    (4, logging.DEBUG),
    (5, logging.DEBUG)
])
def test_init_verbosities(logger_mock, verbosity, level):
    logger = Logger(verbosity=verbosity)
    logger.start_logger.assert_called_with(level)
    logger.add_handler.assert_called_with(level, 'stdout')


def test_logger_output(logger_mock):
    logger = Logger(output='mylog')
    logger.add_handler.assert_called_with(50, 'mylog')


def test_start_logger(mocker):
    mocker.patch.object(logging, 'getLogger')
    logger = Logger()
    logging.getLogger.assert_called_with('magnivore')
    logging.getLogger().setLevel.assert_called_with(logging.CRITICAL)
    assert logger.logger == logging.getLogger()


def test_add_handler(mocker):
    mocker.patch.object(logging, 'FileHandler')
    mocker.patch.object(logging, 'getLogger')
    logger = Logger(output='mylog')
    logging.FileHandler.assert_called_with('mylog')
    logging.FileHandler().setLevel.assert_called_with(logging.CRITICAL)
    logging.getLogger().addHandler.assert_called_with(logging.FileHandler())
    assert isinstance(logger, Logger)


def test_log(logger):
    logger.events = {'my-event': ('info', 'hello {}')}
    logger.log('my-event', 'world')
    logger.logger.log.assert_called_with(logging.INFO, 'hello world')


def test_log_custom_event(logger):
    logger.events = {}
    logger.log('my-event', 'world')
    logger.logger.log.assert_called_with(logging.INFO, 'my-event')
