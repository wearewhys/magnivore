# -*- coding: utf-8 -*-
import re
from decimal import Decimal
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

    @classmethod
    def _dot_reduce(cls, rule_from, target):
        """
        A shorthand for _dot and reduce.
        """
        return reduce(cls._dot, rule_from.split('.'), target)

    @classmethod
    def basic(cls, rule, target):
        """
        The basic-most rule, which simply produces the requested value.
        """
        return cls._dot_reduce(rule, target)

    @classmethod
    def factor(cls, rule, target):
        """
        The factor rule multiplies the value by a factor.
        """
        value = cls._dot_reduce(rule['from'], target)
        original_type = type(value)
        return original_type(Decimal(value) * Decimal(rule['factor']))

    @classmethod
    def format(cls, rule, target):
        """
        The format rule produces a formatted string.
        """
        rule_from = rule['from']
        format_data = []

        if type(rule_from) == list:
            for i in rule_from:
                old_value = cls._dot_reduce(i, target)
                format_data.append(old_value)

        if type(rule_from) == str:
            old_value = cls._dot_reduce(rule_from, target)
            format_data.append(old_value)
        return rule['format'].format(*format_data)

    @classmethod
    def match(cls, rule, target, logger):
        """
        Match rule
        """
        old_value = cls._dot_reduce(rule['match'], target)
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

    @classmethod
    def expression(cls, rule, target, logger):
        """
        The expression rule runs a regular expression against the specified
        column.
        """
        attribute = cls._dot_reduce(rule['from'], target)
        result = re.findall(rule['expression'], attribute)
        if result:
            return result[0]
        logger.log('expression-notfound', rule, target)
