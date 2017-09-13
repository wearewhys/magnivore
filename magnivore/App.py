# -*- coding: utf-8 -*-
import ujson

from .Logger import Logger
from .RulesParser import RulesParser


class App:
    """
    Gets the components together and provides clean access to features.
    """

    @staticmethod
    def run(rules_file='rules.json', verbosity=0):
        """
        Runs the parser with a given rules file.
        """
        logger = Logger(verbosity=verbosity)
        logger.log('run-verbosity', verbosity)
        rules = {}
        with open(rules_file, 'r') as f:
            rules = ujson.load(f)
        RulesParser(logger).parse(rules)
