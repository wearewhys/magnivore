# -*- coding: utf-8 -*-
from magnivore.Logger import Logger
from magnivore.RulesParser import RulesParser

from pytest import fixture


@fixture
def rules():
    rules = {
        'profiles': {
            'joins': [
                {'table': 'users'},
                {'table': 'addresses', 'on': 'user'}
            ],
            'transform': {
                'name': 'username',
                'city': 'addresses.city'
            }
        }
    }
    return rules


@fixture
def logger():
    return Logger()


def test_transform(logger, config_setup, donor_setup, receiver_setup, rules):
    rules_parser = RulesParser(logger, configfile='magnivore-test.json')
    rules_parser.parse(rules)
    profiles = receiver_setup[0].select()
    assert profiles[0].name == 'gandalf'
    assert profiles[0].city == 'shire'
    assert profiles[1].name == 'saruman'
    assert profiles[1].city == 'orthanc'
    assert profiles[2].name == 'elrond'
    assert profiles[2].city == 'rivendell'


def test_transform_track(logger, config_setup, donor_setup, receiver_setup,
                         tracker_setup, rules):
    rules['profiles']['track'] = 'editor'
    rules_parser = RulesParser(logger, configfile='magnivore-test.json')
    rules_parser.parse(rules)
    profiles = receiver_setup[0].select().where(receiver_setup[0].id > 3)
    users = donor_setup[0].select()
    results = tracker_setup.select().where(tracker_setup.match == 'editor')
    assert results[0].new == profiles[0].id
    assert results[0].old == users[0].id
    assert results[1].new == profiles[1].id
    assert results[1].old == users[1].id
    assert results[2].new == profiles[2].id
    assert results[2].old == users[2].id


def test_transform_match(logger, config_setup, donor_setup, receiver_setup,
                         tracker_setup, rules):
    rules['profiles']['track'] = 'editor'
    article_rules = {
        'articles': {
            'joins': [
                {'table': 'posts'}
            ],
            'transform': {
                'title': 'title',
                'author': {
                    'match': 'editor'
                }
            }
        }
    }
    rules_parser = RulesParser(logger, configfile='magnivore-test.json')
    rules_parser.parse(rules)
    rules_parser.parse(article_rules)
    articles = receiver_setup[1].select()
    tracks = tracker_setup.select().where(tracker_setup.match == 'editor')
    assert articles[0].author.id == tracks[0].new
    assert articles[1].author.id == tracks[1].new
    assert articles[2].author.id == tracks[2].new
