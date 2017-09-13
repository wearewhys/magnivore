# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from magnivore.Lexicon import Lexicon
from magnivore.Transformer import Transformer

from pytest import fixture


@fixture
def transformations():
    return {
        'profilefield': 'nodesfield'
    }


@fixture
def transformer(transformations, logger):
    return Transformer(transformations, MagicMock(), logger, match='match')


def test_init(logger):
    assert Transformer(None, None, logger).match is None


def test_init_match(logger):
    assert Transformer(None, None, logger, 'match').match == 'match'


def test_item_values(mocker, transformer):
    mocker.patch.object(Lexicon, 'basic')
    target = MagicMock()
    values = transformer.item_values(target)
    Lexicon.basic.assert_called_with('nodesfield', target)
    assert values['profilefield'] == Lexicon.basic()


def test_item_values_transform(mocker, transformer):
    mocker.patch.object(Lexicon, 'transform')
    transformations = {
        'age': {
            'transform': {}
        }
    }
    transformer.transformations = transformations
    target = MagicMock()
    values = transformer.item_values(target)
    Lexicon.transform.assert_called_with(transformations['age'], target)
    assert values['age'] == Lexicon.transform()


def test_item_values_format(mocker, transformer):
    mocker.patch.object(Lexicon, 'format')
    transformations = {
        'age': {
            'format': {}
        }
    }
    transformer.transformations = transformations
    target = MagicMock()
    values = transformer.item_values(target)
    Lexicon.format.assert_called_with(transformations['age'], target)
    assert values['age'] == Lexicon.format()


def test_item_values_match(mocker, transformer, logger):
    mocker.patch.object(Lexicon, 'match')
    transformations = {
        'age': {
            'match': {}
        }
    }
    transformer.transformations = transformations
    target = MagicMock()
    values = transformer.item_values(target)
    Lexicon.match.assert_called_with(transformations['age'], target, logger)
    assert values['age'] == Lexicon.match()


def test_item_values_match_none(mocker, transformer):
    mocker.patch.object(Lexicon, 'match')
    Lexicon.match.return_value = None
    transformations = {
        'age': {
            'match': {}
        }
    }
    transformer.transformations = transformations
    assert transformer.item_values(MagicMock()) is None


def test_item_values_static(mocker, transformer):
    mocker.patch.object(Lexicon, 'static')
    transformations = {
        'age': {
            'static': {}
        }
    }
    target = MagicMock()
    transformer.transformations = transformations
    values = transformer.item_values(target)
    Lexicon.static.assert_called_with(transformations['age'], target)
    assert values['age'] == Lexicon.static()


def test_item_values_expression(mocker, transformer, logger):
    mocker.patch.object(Lexicon, 'expression')
    transformations = {
        'age': {
            'expression': {}
        }
    }
    target = MagicMock()
    transformer.transformations = transformations
    values = transformer.item_values(target)
    Lexicon.expression.assert_called_with(transformations['age'], target,
                                          logger)
    assert values['age'] == Lexicon.expression()


def test_transform(mocker, transformer):
    mocker.patch.object(Transformer, 'item_values')
    target = MagicMock()
    result = transformer.transform(target)
    Transformer.item_values.assert_called_with(target)
    assert result.save.call_count == 1


def test_transform_none(mocker, transformer):
    mocker.patch.object(Transformer, 'item_values')
    Transformer.item_values.return_value = None
    target = MagicMock(id=100)
    result = transformer.transform(target)
    assert result is None


def test_sync(mocker, transformer, logger):
    mocker.patch.object(Transformer, 'item_values')
    mocker.patch.object(Transformer, '_set_values')
    mocker.patch.object(Lexicon, 'sync')
    target = MagicMock()
    result = transformer.sync(target)
    Transformer.item_values.assert_called_with(target)
    Lexicon.sync.assert_called_with('match', target, logger)
    assert Transformer._set_values.call_count == 1
    assert result == transformer.model.get()
    assert result.save.call_count == 1


def test_sync_none(mocker, transformer, logger):
    mocker.patch.object(Transformer, 'item_values')
    mocker.patch.object(Transformer, '_set_values')
    mocker.patch.object(Lexicon, 'sync')
    Lexicon.sync.return_value = None
    assert transformer.sync(MagicMock()) is None
