# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, call

from magnivore.Targets import Targets

from peewee import fn
from pytest import fixture, raises


@fixture
def nodes():
    return MagicMock()


@fixture
def nodes_query(nodes):
    return nodes.select()


@fixture
def points():
    return MagicMock()


@fixture
def targets(nodes, points, logger):
    source_models = {'nodes': nodes, 'points': points}
    targets = Targets(source_models, logger)
    return targets


@fixture
def joins():
    joins = [
        {'table': 'nodes'},
        {'table': 'points', 'on': 'node'}
    ]
    return joins


@fixture(params=['gt', 'lt', 'not'])
def operator(request, nodes):
    nodes.somefield = 'string'
    if request.param == 'gt':
        expression = (nodes.somefield > 'myvalue')
    elif request.param == 'lt':
        expression = (nodes.somefield < 'myvalue')
    else:
        expression = (nodes.somefield != 'myvalue')
    return [request.param, expression]


def test_get_targets_empty(targets):
    with raises(ValueError):
        targets.get([])


def test_get(targets, joins, nodes, nodes_query, points):
    targets.get(joins)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.join.assert_called_with(points, on=points.node)
    assert nodes_query.join().execute.call_count == 1


def test_get_triple_join(targets, joins, nodes, nodes_query, points):
    dots = MagicMock()
    targets.source_models['dots'] = dots
    joins.append({'table': 'dots', 'on': ['id', 'point']})
    targets.get(joins)
    nodes_query.join().join.assert_called_with(dots, on=False)
    assert nodes_query.join().join().execute.call_count == 1


def test_get_limit(targets, joins, nodes, nodes_query, points):
    targets.get(joins, limit=100)
    nodes_query.join().limit.assert_called_with(100)
    assert nodes_query.join().limit().offset().execute.call_count == 1


def test_get_limit_with_offset(targets, joins, nodes, nodes_query, points):
    targets.get(joins, limit=100, offset=10)
    nodes_query.join().limit().offset.assert_called_with(10)
    assert nodes_query.join().limit().offset().execute.call_count == 1


def test_get_switch(targets, joins, nodes, nodes_query, points):
    joins[1]['switch'] = True
    targets.get(joins)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.switch().join.assert_called_with(points, on=points.node)
    assert nodes_query.switch().join().execute.call_count == 1


def test_get_join_on(targets, joins, nodes, nodes_query, points):
    joins[1]['on'] = ['id', 'node']
    targets.get(joins)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.join.assert_called_with(points, on=(nodes.id == points.node))
    assert nodes_query.join().execute.call_count == 1


def test_get_join_outer(targets, joins, nodes, nodes_query, points):
    joins[1]['outer'] = True
    targets.get(joins)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.join.assert_called_with(points, 'LEFT OUTER', on=points.node)
    assert nodes_query.join().execute.call_count == 1


def test_get_conditions(targets, joins, nodes, nodes_query):
    joins[0]['conditions'] = {
        'somefield': 'myvalue'
    }
    joins[1]['conditions'] = {
        'somefield': 'myvalue'
    }
    targets.get(joins)
    expression = (nodes.somefield == 'myvalue')
    nodes_query.join().where().where.assert_called_with(expression)
    assert nodes_query.join().where().where().execute.call_count == 1


def test_get_conditions_greater(operator, targets, joins, nodes, nodes_query):
    joins[0]['conditions'] = {
        'somefield': {
            'operator': operator[0],
            'value': 'myvalue'
        }
    }
    targets.get(joins)
    nodes_query.join().where.assert_called_with(operator[1])
    assert nodes_query.join().where().execute.call_count == 1


def test_get_conditions_in(targets, joins, nodes, nodes_query):
    joins[0]['conditions'] = {
        'somefield': {
            'operator': 'in',
            'value': ['myvalue']
        }
    }
    targets.get(joins)
    expression = (nodes.somefield << ['myvalue'])
    nodes_query.join().where.assert_called_with(expression)
    assert nodes_query.join().where().execute.call_count == 1


def test_get_conditions_isnull(targets, joins, nodes, nodes_query):
    joins[0]['conditions'] = {
        'somefield': {
            'operator': 'isnull',
            'value': True
        }
    }
    targets.get(joins)
    expression = (nodes.somefield.is_null(True))
    nodes_query.join().where.assert_called_with(expression)
    assert nodes_query.join().where().execute.call_count == 1


def test_get_aggregations(mocker, targets, joins, nodes, nodes_query):
    mocker.patch.object(fn, 'Count')
    fn.Count.return_value = 0
    joins[0]['aggregation'] = {
        'function': 'count',
        'group': 'email',
        'condition': {
            'operator': 'gt',
            'value': 1
        }
    }
    targets.get(joins)
    nodes_query.join().group_by.assert_called_with(nodes.email)
    nodes_query.join().group_by().having.assert_called_with(fn.Count() > 1)
    assert nodes_query.join().group_by().having().execute.call_count == 1


def test_get_aggregations_eq(mocker, targets, joins, nodes, nodes_query):
    mocker.patch.object(fn, 'Count')
    fn.Count.return_value = 0
    joins[0]['aggregation'] = {
        'function': 'count',
        'group': 'email',
        'condition': {
            'operator': 'eq',
            'value': 1
        }
    }
    targets.get(joins)
    nodes_query.join().group_by.assert_called_with(nodes.email)
    nodes_query.join().group_by().having.assert_called_with(fn.Count() == 1)
    assert nodes_query.join().group_by().having().execute.call_count == 1


def test_get_log_query(targets, joins, nodes_query, logger):
    targets.get(joins)
    calls = [call.logger.log('get-targets', nodes_query.join())]
    logger.log.assert_has_calls(calls)


def test_get_log_targets_count(targets, joins, nodes_query, logger):
    targets.get(joins)
    calls = [call.logger.log('get-targets-count', nodes_query.join().count())]
    logger.log.assert_has_calls(calls)
