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
def sources():
    sources = [
        {'table': 'nodes'},
        {'table': 'points', 'on': 'node'}
    ]
    return sources


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


def test_get(targets, sources, nodes, nodes_query, points):
    targets.get(sources)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.join.assert_called_with(points, on=points.node)
    assert nodes_query.join().execute.call_count == 1


def test_get_triple_join(targets, sources, nodes, nodes_query, points):
    dots = MagicMock()
    targets.source_models['dots'] = dots
    sources.append({'table': 'dots', 'on': ['id', 'point']})
    targets.get(sources)
    nodes_query.join().join.assert_called_with(dots, on=False)
    assert nodes_query.join().join().execute.call_count == 1


def test_get_limit(targets, sources, nodes, nodes_query, points):
    targets.get(sources, limit=100)
    nodes_query.join().limit.assert_called_with(100)
    assert nodes_query.join().limit().offset().execute.call_count == 1


def test_get_limit_with_offset(targets, sources, nodes, nodes_query, points):
    targets.get(sources, limit=100, offset=10)
    nodes_query.join().limit().offset.assert_called_with(10)
    assert nodes_query.join().limit().offset().execute.call_count == 1


def test_get_switch(targets, sources, nodes, nodes_query, points):
    sources[1]['switch'] = True
    targets.get(sources)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.switch().join.assert_called_with(points, on=points.node)
    assert nodes_query.switch().join().execute.call_count == 1


def test_get_join_on(targets, sources, nodes, nodes_query, points):
    sources[1]['on'] = ['id', 'node']
    targets.get(sources)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.join.assert_called_with(points, on=(nodes.id == points.node))
    assert nodes_query.join().execute.call_count == 1


def test_get_join_outer(targets, sources, nodes, nodes_query, points):
    sources[1]['outer'] = True
    targets.get(sources)
    nodes.select.assert_called_with(nodes, points)
    nodes_query.join.assert_called_with(points, 'LEFT OUTER', on=points.node)
    assert nodes_query.join().execute.call_count == 1


def test_get_conditions(targets, sources, nodes, nodes_query):
    sources[0]['conditions'] = {
        'somefield': 'myvalue'
    }
    sources[1]['conditions'] = {
        'somefield': 'myvalue'
    }
    targets.get(sources)
    expression = (nodes.somefield == 'myvalue')
    nodes_query.join().where().where.assert_called_with(expression)
    assert nodes_query.join().where().where().execute.call_count == 1


def test_get_conditions_greater(operator, targets, sources, nodes):
    sources[0]['conditions'] = {
        'somefield': {
            'operator': operator[0],
            'value': 'myvalue'
        }
    }
    targets.get(sources)
    nodes.select().join().where.assert_called_with(operator[1])
    assert nodes.select().join().where().execute.call_count == 1


def test_get_conditions_in(targets, sources, nodes, nodes_query):
    sources[0]['conditions'] = {
        'somefield': {
            'operator': 'in',
            'value': ['myvalue']
        }
    }
    targets.get(sources)
    expression = (nodes.somefield << ['myvalue'])
    nodes_query.join().where.assert_called_with(expression)
    assert nodes_query.join().where().execute.call_count == 1


def test_get_conditions_isnull(targets, sources, nodes, nodes_query):
    sources[0]['conditions'] = {
        'somefield': {
            'operator': 'isnull',
            'value': True
        }
    }
    targets.get(sources)
    expression = (nodes.somefield.is_null(True))
    nodes_query.join().where.assert_called_with(expression)
    assert nodes_query.join().where().execute.call_count == 1


def test_get_aggregations(mocker, targets, sources, nodes, nodes_query):
    mocker.patch.object(fn, 'Count')
    fn.Count.return_value = 0
    sources[0]['aggregation'] = {
        'function': 'count',
        'group': 'email',
        'condition': {
            'operator': 'gt',
            'value': 1
        }
    }
    targets.get(sources)
    nodes_query.join().group_by.assert_called_with(nodes.email)
    nodes_query.join().group_by().having.assert_called_with(fn.Count() > 1)
    assert nodes_query.join().group_by().having().execute.call_count == 1


def test_get_aggregations_eq(mocker, targets, sources, nodes, nodes_query):
    mocker.patch.object(fn, 'Count')
    fn.Count.return_value = 0
    sources[0]['aggregation'] = {
        'function': 'count',
        'group': 'email',
        'condition': {
            'operator': 'eq',
            'value': 1
        }
    }
    targets.get(sources)
    nodes_query.join().group_by.assert_called_with(nodes.email)
    nodes_query.join().group_by().having.assert_called_with(fn.Count() == 1)
    assert nodes_query.join().group_by().having().execute.call_count == 1


def test_get_picks(targets, sources, nodes, nodes_query):
    sources[0]['picks'] = {
        'field': True
    }
    targets.get(sources)
    nodes.select.assert_called_with(nodes.field)
    assert nodes_query.join().execute.call_count == 1


def test_get_picks_sum(targets, sources, nodes, nodes_query):
    sources[0]['picks'] = {
        'field': 'sum'
    }
    targets.get(sources)
    nodes.select.assert_called_with(fn.Sum(nodes.field))
    assert nodes_query.join().execute.call_count == 1


def test_get_log_query(targets, sources, nodes_query, logger):
    targets.get(sources)
    calls = [call.logger.log('get-targets', nodes_query.join())]
    logger.log.assert_has_calls(calls)


def test_get_log_targets_count(targets, sources, nodes_query, logger):
    targets.get(sources)
    calls = [call.logger.log('get-targets-count', nodes_query.join().count())]
    logger.log.assert_has_calls(calls)
