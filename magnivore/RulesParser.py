# -*- coding: utf-8 -*-
from .Config import Config
from .Interface import Interface
from .Targets import Targets
from .Tracker import Tracker, tracker_interface
from .Transformer import Transformer


class RulesParser():
    """
    The RulesParser class takes care of parsing the rules and making operations
    accordingly
    """

    def __init__(self, logger, configfile='magnivore.json'):
        self.config = Config(filename=configfile)
        self.interface = Interface(self.config.get())
        self.receiver = self.interface.receiver()
        self.targets = Targets(self.interface.donor(), logger)
        self.logger = logger

    def _process(self, table, table_rules):
        model = self.receiver[table]
        targets = self.targets.get(table_rules['sources'])

        if 'transform' in table_rules:
            transformations = table_rules['transform']
            transformer = Transformer(transformations, model, self.logger)
            for target in targets:
                item = transformer.transform(target)
                if item:
                    if 'track' in table_rules:
                        Tracker.track(table_rules['track'], target, item)

        if 'sync' in table_rules:
            sync = table_rules['sync-transform']
            match = table_rules['sync']
            transformer = Transformer(sync, model, self.logger, match=match)
            for target in targets:
                transformer.sync(target)

    def parse(self, rules):
        """
        Transforms data from a schema to another, using a given ruleset.
        """
        for table in rules:
            self.logger.log('parse-table', table)
            if type(rules[table]) == list:
                for element in rules[table]:
                    if 'label' in element:
                        self.logger.log('parse-ruleset', element['label'])
                    self._process(table, element)
                    self.interface.commit()
                    tracker_interface.commit()
            else:
                self._process(table, rules[table])
                self.interface.commit()
                tracker_interface.commit()
