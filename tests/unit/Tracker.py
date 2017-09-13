# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from magnivore.Tracker import Tracker

from peewee import CharField, IntegerField

from pytest import fixture


@fixture
def tracker(mocker):
    mocker.patch.object(Tracker, 'get')
    mocker.patch.object(Tracker, 'save')


def test_tracker():
    assert isinstance(Tracker.new, IntegerField)
    assert isinstance(Tracker.old, IntegerField)
    assert isinstance(Tracker.match, CharField)


def test_tracker_track(tracker):
    old_item = MagicMock(id=1)
    new_item = MagicMock(id=2)
    result = Tracker.track('name', old_item, new_item)
    assert Tracker.save.call_count == 1
    assert result.match == 'name'
    assert result.old == 1
    assert result.new == 2


def test_tracker_find_match(tracker):
    result = Tracker.find_match('match_name', 100)
    match_expression = (Tracker.match == 'match_name')
    old_expression = (Tracker.old == 100)
    assert result == Tracker.get(match_expression, old_expression)


def test_tracker_match_not_found(tracker):
    Tracker.get.side_effect = Tracker.DoesNotExist()
    assert Tracker.find_match('match_name', 100) is None
