# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from magnivore.Interface import Interface

from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase

from playhouse.reflection import Introspector

from pytest import fixture, mark


@fixture
def interface(mocker, config):
    mocker.patch.object(SqliteDatabase, 'begin')
    return Interface(config)


@mark.parametrize('name, db_type, instance', [
    ('magnivore', 'postgres', PostgresqlDatabase),
    ('magnivore', 'mysql', MySQLDatabase)
])
def test_create_database(interface, name, db_type, instance):
    interface.create_database(name, db_type, {})
    database = interface.databases[name]
    assert isinstance(database, instance)
    assert database.autocommit is False


def test_create_database_sqlite(interface):
    interface.create_database('magnivore')
    database = interface.databases['magnivore']
    assert isinstance(database, SqliteDatabase)
    assert database.autocommit is False
    assert database.begin.call_count == 1


def test_create_database_no_type(interface):
    interface.create_database('magnivore', 'wrong', {})
    database = interface.databases['magnivore']
    assert isinstance(database, SqliteDatabase)
    assert database.autocommit is False


def test_commit(interface):
    interface.databases['test'] = MagicMock()
    interface.commit()
    assert interface.databases['test'].commit.call_count == 1
    assert interface.databases['test'].begin.call_count == 1


def test_string_special(interface):
    interface.id = None
    assert interface.string_special() == 'Interface:None'


@mark.parametrize('method', ['donor', 'receiver'])
def test_donor_and_receiver_result(mocker, method, config, interface):
    mocker.patch.object(Introspector, 'from_database')
    model = type('model', (object,), {})
    Introspector.from_database().generate_models.return_value = {'m': model}
    result = getattr(interface, method)()
    assert result == {'m': model}
    assert model.__str__ == Interface.string_special


@mark.parametrize('method', ['donor', 'receiver'])
def test_donor_and_receiver_db(mocker, method, config, interface):
    mocker.patch.object(Interface, 'create_database')
    interface.databases = {'receiver.db': MagicMock(), 'donor.db': MagicMock()}
    getattr(interface, method)()
    db_config = config[method]
    Interface.create_database.assert_called_with(db_config['name'],
                                                 db_type=db_config['type'],
                                                 auth=db_config['auth'])
