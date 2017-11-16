# -*- coding: utf-8 -*-
import re
from functools import reduce

from .Tracker import Tracker


class Lexicon:
    """
    A lexicon of parsing rules that can be used by various parser to apply
    rules uniformely.
    """

    @staticmethod
    def _dot(item, attribute):
        try:
            return getattr(item, attribute)
        except AttributeError:
            return None

    @staticmethod
    def _dot_reduce(rule_from, target):
        """
        A shorthand for _dot and reduce.
        """
        return reduce(Lexicon._dot, rule_from.split('.'), target)

    @staticmethod
    def basic(rule, target):
        """
        The basic-most rule, which simply produces the requested value.
        """
        return Lexicon._dot_reduce(rule, target)

    @staticmethod
    def factor(rule, target):
        """
        The factor rule multiplies the value by a factor.
        """
        value = Lexicon._dot_reduce(rule['from'], target)
        return value * rule['factor']

    @staticmethod
    def format(rule, target):
        """
        The format rule produces a formatted string.
        """
        rule_from = rule['from']
        format_data = []

        if type(rule_from) == list:
            for i in rule_from:
                old_value = Lexicon._dot_reduce(i, target)
                format_data.append(old_value)

        if type(rule_from) == str:
            old_value = Lexicon._dot_reduce(rule_from, target)
            format_data.append(old_value)
        return rule['format'].format(*format_data)

    @staticmethod
    def match(rule, target, logger):
        """
        Match rule
        """
        old_value = Lexicon._dot_reduce(rule['match'], target)
        match_name = rule['match']
        if 'from' in rule:
            match_name = rule['from']

        match = Tracker.find_match(match_name, old_value)
        if match:
            return match.new
        logger.log('match-notfound', rule, target)

    @staticmethod
    def sync(rule, target, logger):
        """
        Sync rule
        """
        old_value = getattr(target, rule['attribute'])
        match = Tracker.find_match(rule['from'], old_value)
        if match is None:
            logger.log('sync-notfound', rule, target)
            return None
        return match.new

    @staticmethod
    def static(rule, target):
        """
        The static rule produces a constant value.
        """
        return rule['static']

    @staticmethod
    def transform(rule, target):
        """
        The transform rule produces different values based on the target's
        value.
        """
        return rule['transform'][getattr(target, rule['from'])]

    @staticmethod
    def expression(rule, target, logger):
        """
        The expression rule runs a regular expression against the specified
        column.
        """
        attribute = Lexicon._dot_reduce(rule['from'], target)
        result = re.findall(rule['expression'], attribute)
        if result:
            return result[0]
        logger.log('expression-notfound', rule, target)
