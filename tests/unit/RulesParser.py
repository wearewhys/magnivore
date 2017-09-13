# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from magnivore.Interface import Interface
from magnivore.RulesParser import RulesParser
from magnivore.Targets import Targets
from magnivore.Tracker import Tracker, tracker_interface
from magnivore.Transformer import Transformer

from pytest import fixture


@fixture
def rules():
    rules = {
        'profiles': {
            'joins': [
                {'table': 'nodes'},
                {'table': 'points', 'on': 'node'}
            ],
            'transform': {
                'profilefield': 'nodesfield'
            }
        }
    }
    return rules


@fixture
def list_rules(rules):
    rules['profiles'] = [rules['profiles'], rules['profiles']]
    return rules


@fixture
def nodes():
    return MagicMock()


@fixture
def points():
    return MagicMock()


@fixture
def rules_parser(mocker, parser_dependencies, nodes, points, logger):
    mocker.patch.object(Interface, 'commit')
    mocker.patch.object(tracker_interface, 'commit')
    Interface.donor.return_value = {'nodes': nodes, 'points': points}
    Interface.receiver.return_value = {'profiles': MagicMock()}
    return RulesParser(logger)


@fixture
def targets(mocker):
    mocker.patch.object(Targets, 'get')
    targets_list = [MagicMock()]
    Targets.get.return_value = targets_list
    return targets_list


def test_rules_parser_init_configfile(parser_dependencies):
    RulesParser(None, configfile='whatever.json')


def test_parse(rules_parser, targets, rules):
    rules_parser.parse(rules)
    Transformer.transform.assert_called_with(targets[0])
    assert Interface.commit.call_count == 1
    assert tracker_interface.commit.call_count == 1


def test_parse_list(rules_parser, targets, list_rules):
    rules_parser.parse(list_rules)
    Transformer.transform.assert_called_with(targets[0])
    assert Interface.commit.call_count == 2
    assert tracker_interface.commit.call_count == 2


def test_parse_track(rules_parser, targets, rules):
    rules['profiles']['track'] = 'trackingname'
    rules_parser.parse(rules)
    old_target = targets[0]
    new_item = Transformer.transform()
    Tracker.track.assert_called_with('trackingname', old_target, new_item)


def test_parse_track_none(rules_parser, targets, rules):
    Transformer.transform.return_value = None
    rules['profiles']['track'] = 'trackingname'
    rules_parser.parse(rules)
    assert Tracker.track.call_count == 0


def test_parse_sync(mocker, rules_parser, targets, rules):
    mocker.patch.object(Transformer, 'sync')
    rules['profiles']['sync-transform'] = rules['profiles']['transform']
    rules['profiles']['sync'] = 'trackingname'
    del rules['profiles']['transform']
    rules_parser.parse(rules)
    Transformer.sync.assert_called_with(targets[0])


def test_parse_log_table(rules_parser, logger, targets, rules):
    rules_parser.parse(rules)
    logger.log.assert_called_with('parse-table', 'profiles')


def test_parse_log_label(rules_parser, logger, targets, list_rules):
    list_rules['profiles'][0]['label'] = 'label'
    list_rules['profiles'][1]['label'] = 'label'
    rules_parser.parse(list_rules)
    logger.log.assert_called_with('parse-ruleset', 'label')
