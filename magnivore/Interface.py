# -*- coding: utf-8 -*-
from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase

from playhouse.reflection import Introspector


class Interface:
    """
    The Interface provides interaction with database and models.
    """
    def __init__(self, config):
        self.config = config
        self.databases = {}

    def _generate_models(self, db_config):
        name = db_config['name']
        self.create_database(name, db_type=db_config['type'],
                             auth=db_config['auth'])
        introspector = Introspector.from_database(self.databases[name])
        models = introspector.generate_models()
        for (name, model) in models.items():
            model.__str__ = Interface.string_special
        return models

    def create_database(self, name, db_type='sqlite', auth=None):
        """
        Creates a databases dynamically and registers it
        """
        if db_type == 'postgres':
            auth['autocommit'] = False
            self.databases[name] = PostgresqlDatabase(name, **auth)
        elif db_type == 'mysql':
            auth['autocommit'] = False
            self.databases[name] = MySQLDatabase(name, **auth)
        else:
            self.databases[name] = SqliteDatabase(name, autocommit=False)
            self.databases[name].begin()

    def commit(self):
        """
        Commits all transactions to all databases
        """
        for key, database in self.databases.items():
            database.commit()
            database.begin()

    def string_special(self):
        """
        Used to override __str__ in generated models.
        """
        return '{}:{}'.format(self.__class__.__name__, self.id)

    def donor(self):
        """
        Provides a list of donor models
        """
        return self._generate_models(self.config['donor'])

    def receiver(self):
        """
        Provides a list of receiver models
        """
        return self._generate_models(self.config['receiver'])
