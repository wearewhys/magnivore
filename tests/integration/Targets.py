# -*- coding: utf-8 -*-
from magnivore.Interface import Interface
from magnivore.Logger import Logger
from magnivore.Targets import Targets

from pytest import fixture


@fixture
def interface(config_setup):
    interface = Interface(config_setup.get())
    return interface


def test_get(interface, donor_setup, receiver_setup, tracker_setup):
    targets = Targets(interface.donor(), Logger())
    sources = [
        {'table': 'users'},
        {'table': 'addresses', 'on': 'user'}
    ]
    items = targets.get(sources)
    results = []
    for item in items:
        results.append(item)
    assert results[0].username == 'gandalf'
    assert results[0].addresses.city == 'shire'
    assert results[1].username == 'saruman'
    assert results[1].addresses.city == 'orthanc'
    assert results[2].username == 'elrond'
    assert results[2].addresses.city == 'rivendell'
