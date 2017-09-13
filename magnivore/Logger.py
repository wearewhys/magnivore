# -*- coding: utf-8 -*-
import logging


class Logger:

    verbosities = ['critical', 'error', 'warning', 'info', 'debug']
    events = {
        'run-verbosity': ('debug', 'Running with verbosity level {}'),
        'get-targets': ('debug', 'Retrieving items with query: {}'),
        'parse-table': ('info', 'Parsing table {}'),
        'parse-ruleset': ('info', 'Parsing {} ruleset'),
        'get-targets-count': ('info', 'Found {} items'),
        'match-notfound': ('warning', 'Match rule {} on {} has no matches'),
        'expression-notfound': ('warning', 'Expression rule {} on {} is null'),
        'sync-notfound': ('warning', 'Sync rule {} on {} has no matches')
    }

    def __init__(self, *args, verbosity=0, output='stdout'):
        level = self._level_from_verbosity(verbosity)
        self.start_logger(level)
        self.add_handler(level, output)

    def _level_from_verbosity(self, verbosity):
        if verbosity >= len(self.verbosities):
            verbosity = len(self.verbosities) - 1
        return getattr(logging, self.verbosities[verbosity].upper())

    def start_logger(self, level):
        logging.basicConfig(level=level)
        for key in logging.Logger.manager.loggerDict:
            logging.getLogger(key).setLevel(logging.CRITICAL)
        self.logger = logging.getLogger('magnivore')

    def add_handler(self, level, output):
        if output != 'stdout':
            handler = logging.FileHandler(output)
            handler.setLevel(level)
            self.logger.addHandler(handler)

    def log(self, event, *args):
        message = event
        level = logging.INFO
        if event in self.events:
            level = getattr(logging, self.events[event][0].upper())
            message = self.events[event][1]
        self.logger.log(level, message.format(*args))
