# -*- coding: utf-8 -*-
from magnivore.Interface import Interface

from peewee import SqliteDatabase


def test_init_db(config_setup):
    interface = Interface(config_setup.get())
    interface.create_database('donor.db')
    assert isinstance(interface.databases['donor.db'], SqliteDatabase)


def test_donor(config_setup, donor_teardown):
    interface = Interface(config_setup.get())
    assert interface.donor() == {}


def test_receiver(config_setup, receiver_teardown):
    interface = Interface(config_setup.get())
    assert interface.receiver() == {}
