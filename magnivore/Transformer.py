# -*- coding: utf-8 -*-
from .Lexicon import Lexicon


class Transformer():

    def __init__(self, transformations, model, logger, match=None):
        self.transformations = transformations
        self.model = model
        self.match = match
        self.logger = logger

    def item_values(self, target):
        """
        Finds the values of an item using given transformations.
        """
        values = {}
        for to_field, rule in self.transformations.items():
            rule_type = type(rule)
            if rule_type == str:
                value = Lexicon.basic(rule, target)
            elif 'transform' in rule:
                value = Lexicon.transform(rule, target)
            elif 'format' in rule:
                value = Lexicon.format(rule, target)
            elif 'match' in rule:
                value = Lexicon.match(rule, target, self.logger)
                if value is None:
                    return None
            elif 'static' in rule:
                value = Lexicon.static(rule, target)
            elif 'expression' in rule:
                value = Lexicon.expression(rule, target, self.logger)
            values[to_field] = value
        return values

    def transform(self, target):
        """
        Transforms a single item.
        """
        values = self.item_values(target)
        if values:
            item = self.model(**values)
            item.save()
            return item

    def _set_values(self, values, item):
        for to_field, value in values.items():
            setattr(item, to_field, value)

    def sync(self, target):
        """
        Synchronizes an existing item
        """
        # TODO(vesuvium): write an integration test that uses this path
        match_id = Lexicon.sync(self.match, target, self.logger)
        if match_id:
            item = self.model.get(self.model.id == match_id)
            self._set_values(self.item_values(target), item)
            item.save()
            return item
