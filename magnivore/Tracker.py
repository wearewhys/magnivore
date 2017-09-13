# -*- coding: utf-8 -*-
from peewee import CharField, IntegerField, Model

from .Interface import Interface


tracker_interface = Interface({})
tracker_interface.create_database('magnivore.db')
database = tracker_interface.databases['magnivore.db']


class Tracker(Model):

    class Meta:
        database = database

    match = CharField()
    old = IntegerField()
    new = IntegerField()

    @staticmethod
    def track(match_name, old_item, new_item):
        item = Tracker(match=match_name, old=old_item.id, new=new_item.id)
        item.save()
        return item

    @staticmethod
    def find_match(match_name, old_id):
        """
        Finds the match for given name and old id
        """
        try:
            return Tracker.get(Tracker.match == match_name,
                               Tracker.old == old_id)
        except Tracker.DoesNotExist:
            return None
