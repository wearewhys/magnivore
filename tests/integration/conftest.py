# -*- coding: utf-8 -*-
import os

from magnivore.Config import Config
from magnivore.Tracker import Tracker, database as tracker_database

from peewee import CharField, ForeignKeyField,  Model, SqliteDatabase

from pytest import fixture

import ujson


donor_database = SqliteDatabase('donor.db')
receiver_database = SqliteDatabase('receiver.db')


class DonorBase(Model):
    class Meta:
        database = donor_database


class ReceiverBase(Model):
    class Meta:
        database = receiver_database


class Users(DonorBase):
    username = CharField()


class Addresses(DonorBase):
    city = CharField()
    user = ForeignKeyField(Users)


class Posts(DonorBase):
    title = CharField()
    editor = ForeignKeyField(Users)


class Profiles(ReceiverBase):
    name = CharField()
    city = CharField()


class Articles(ReceiverBase):
    title = CharField()
    author = ForeignKeyField(Profiles)


@fixture
def config_setup(config, config_teardown):
    with open('magnivore-test.json', 'w') as f:
        ujson.dump(config, f)
    return Config(filename='magnivore-test.json')


@fixture(scope='session')
def donor_teardown(request):
    def teardown():
        os.remove('donor.db')
    request.addfinalizer(teardown)


@fixture(scope='session')
def receiver_teardown(request):
    def teardown():
        os.remove('receiver.db')
    request.addfinalizer(teardown)


@fixture(scope='session')
def tracker_teardown(request):
    def teardown():
        os.remove('magnivore.db')
    request.addfinalizer(teardown)


@fixture(scope='session')
def donor_setup(donor_teardown):
    donor_database.create_tables([Users, Addresses, Posts])
    gandalf = Users(username='gandalf')
    gandalf.save()
    saruman = Users(username='saruman')
    saruman.save()
    elrond = Users(username='elrond')
    elrond.save()
    Addresses(city='shire', user=gandalf).save()
    Addresses(city='orthanc', user=saruman).save()
    Addresses(city='rivendell', user=elrond).save()
    Posts(title='never', editor=gandalf).save()
    Posts(title='gonna', editor=saruman).save()
    Posts(title='let', editor=elrond).save()
    return [Users, Addresses, Posts]


@fixture(scope='session')
def receiver_setup(receiver_teardown):
    receiver_database.create_tables([Profiles, Articles])
    return [Profiles, Articles]


@fixture(scope='session')
def tracker_setup(tracker_teardown):
    tracker_database.create_tables([Tracker])
    return Tracker
