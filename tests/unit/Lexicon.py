# -*- coding: utf-8 -*-
import re
from decimal import Decimal
from unittest.mock import MagicMock

from magnivore.Lexicon import Lexicon
from magnivore.Tracker import Tracker

from pytest import mark


def test_lexicon_basic():
    target = MagicMock()
    result = Lexicon.basic('field', target)
    assert result == target.field


def test_lexicon_basic_dot():
    target = MagicMock()
    result = Lexicon.basic('table.field', target)
    assert result == target.table.field


def test_lexicon_basic_dot_double():
    target = MagicMock()
    result = Lexicon.basic('table.field.nested', target)
    assert result == target.table.field.nested


@mark.parametrize('rule', ['field', 'table.field', 'table.field.nested'])
def test_lexicon_basic_null(rule):
    result = Lexicon.basic(rule, MagicMock(spec=[]))
    assert result is None


@mark.parametrize('target', [
    MagicMock(temperature=10),
    MagicMock(temperature=100)
])
def test_lexicon_transform(target):
    rule = {
        'from': 'temperature',
        'transform': {
            10: 'low',
            100: 'high'
        }
    }
    result = Lexicon.transform(rule, target)
    assert result == rule['transform'][target.temperature]


@mark.parametrize('from_data, target, expected', [
    ('value', MagicMock(value=100), 50),
    ('value', MagicMock(value=Decimal(100)), Decimal(50)),
    ('value', MagicMock(value=100.0), 50.0),
    ('related.value', MagicMock(related=MagicMock(value=100)), 50)
])
def test_lexicon_factor(from_data, target, expected):
    rule = {
        'from': from_data,
        'factor': 0.5
    }
    result = Lexicon.factor(rule, target)
    assert result == expected
    assert type(result) == type(expected)


@mark.parametrize('from_data, format, expected', [
    ('birthyear', '{}-0-0', '1992-0-0'),
    (['birthyear', 'birthmonth'], '{}-{}-0', '1992-9-0')
])
def test_lexicon_format(from_data, format, expected):
    rule = {
        'from': from_data,
        'format': format
    }
    result = Lexicon.format(rule,  MagicMock(birthyear=1992, birthmonth=9))
    assert result == expected


@mark.parametrize('from_data, format, expected', [
    ('rel.birthyear', '{}-0-0', '1992-0-0'),
    (['rel.birthyear', 'rel.birthmonth'], '{}-{}-0', '1992-9-0')
])
def test_lexicon_format_dot(from_data, format, expected):
    rule = {
        'from': from_data,
        'format': format
    }
    related = MagicMock(birthyear=1992, birthmonth=9)
    result = Lexicon.format(rule,  MagicMock(rel=related))
    assert result == expected


def test_lexicon_match(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    rule = {
        'match': 'editor'
    }
    assert Lexicon.match(rule, MagicMock(), logger) == Tracker.find_match().new


def test_lexicon_match_none(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    Tracker.find_match.return_value = None
    rule = {
        'match': 'editor'
    }
    Tracker.find_match.return_value = None
    assert Lexicon.match(rule, MagicMock(), logger) is None


def test_lexicon_match_from(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    rule = {
        'from': 'editor_id',
        'match': 'editor'
    }
    target = MagicMock()
    result = Lexicon.match(rule, target, logger)
    Tracker.find_match.assert_called_with('editor_id', target.editor)
    assert result == Tracker.find_match().new


def test_lexicon_match_dot(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    rule = {
        'from': 'editor_id',
        'match': 'editor.nested'
    }
    target = MagicMock()
    result = Lexicon.match(rule, target, logger)
    Tracker.find_match.assert_called_with('editor_id', target.editor.nested)
    assert result == Tracker.find_match().new


def test_lexicon_match_from_none(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    Tracker.find_match.return_value = None
    rule = {
        'from': 'editor_id',
        'match': 'editor'
    }
    assert Lexicon.match(rule, MagicMock(), logger) is None


def test_lexicon_match_none_log(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    rule = {'match': 'editor'}
    target = MagicMock()
    Tracker.find_match.return_value = None
    Lexicon.match(rule, target, logger)
    logger.log.assert_called_with('match-notfound', rule, target)


def test_lexicon_sync(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    rule = {
        'from': 'editor_id',
        'attribute': 'id'
    }
    target = MagicMock()
    result = Lexicon.sync(rule, target, logger)
    Tracker.find_match.assert_called_with('editor_id', target.id)
    assert result == Tracker.find_match().new


def test_lexicon_sync_none(mocker, logger):
    mocker.patch.object(Tracker, 'find_match')
    Tracker.find_match.return_value = None
    rule = {
        'from': 'editor_id',
        'attribute': 'id'
    }
    target = MagicMock()
    result = Lexicon.sync(rule, target, logger)
    logger.log.assert_called_with('sync-notfound', rule, target)
    assert result is None


def test_lexicon_static():
    rule = {
        'static': 'mymagicvalue'
    }
    result = Lexicon.static(rule, MagicMock())
    assert result == 'mymagicvalue'


def test_lexicon_expression(logger):
    rule = {
        'expression': '(?<=\s).*',
        'from': 'email'
    }
    target = MagicMock(email='clutter email@provider.com')
    result = Lexicon.expression(rule, target, logger)
    assert result == 'email@provider.com'


def test_lexicon_expression_dot(mocker, logger):
    mocker.patch.object(re, 'findall')
    rule = {
        'expression': '(?<=\s).*',
        'from': 'user.email'
    }
    target = MagicMock(email='clutter email@provider.com')
    Lexicon.expression(rule, target, logger)
    re.findall.assert_called_with(rule['expression'], target.user.email)


def test_lexicon_expression_none(logger):
    rule = {
        'expression': '(?<=\s).*',
        'from': 'email'
    }
    target = MagicMock(email='email@provider.com')
    result = Lexicon.expression(rule, target, logger)
    logger.log.assert_called_with('expression-notfound', rule, target)
    assert result is None
