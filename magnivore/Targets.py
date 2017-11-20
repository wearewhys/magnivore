# -*- coding: utf-8 -*-
from peewee import fn


class Targets:

    def __init__(self, source_models, logger):
        self.source_models = source_models
        self.logger = logger

    def _apply_aggregation(self, query, joins):
        model = self.source_models[joins['table']]
        model_field = getattr(model,  joins['aggregation']['group'])
        query = query.group_by(model_field)
        aggregation = joins['aggregation']['function']
        if aggregation == 'count':
            aggregation_function = fn.Count(model_field)
        condition = joins['aggregation']['condition']
        if condition['operator'] == 'gt':
            query = query.having(aggregation_function > condition['value'])
        elif condition['operator'] == 'eq':
            query = query.having(aggregation_function == condition['value'])
        return query

    def _apply_condition(self, query, joins):
        conditions = joins['conditions']
        model = self.source_models[joins['table']]
        for field, condition in conditions.items():
            model_field = getattr(model, field)
            if type(condition) == dict:
                value = condition['value']
                if condition['operator'] == 'not':
                    query = query.where(model_field != value)
                elif condition['operator'] == 'gt':
                    query = query.where(model_field > value)
                elif condition['operator'] == 'lt':
                    query = query.where(model_field < value)
                elif condition['operator'] == 'in':
                    query = query.where(model_field << value)
                elif condition['operator'] == 'isnull':
                    query = query.where(model_field.is_null(value))
            else:
                query = query.where(model_field == condition)
        return query

    def _apply_join(self, query, join, models):
        model = self.source_models[join['table']]

        previous_model = models[models.index(model)-1]
        if 'switch' in join:
            if join['switch']:
                previous_model = models[0]

        on = join['on']
        if type(on) is list:
            left_side = getattr(previous_model, on[0])
            right_side = getattr(model, on[1])
            expression = (left_side == right_side)
        else:
            expression = getattr(model, on)

        if 'switch' in join:
            query = query.switch(models[0])

        if 'outer' in join:
            return query.join(model, 'LEFT OUTER', on=expression)
        return query.join(model, on=expression)

    def _apply_pick(self, query, join):
        model = self.source_models[join['table']]
        selects = []
        for column, value in join['picks'].items():
            if value is True:
                selects.append(getattr(model, column))
            elif value == 'sum':
                selects.append(fn.Sum(getattr(model, column)))
        return query.select(*selects)

    def get(self, joins, limit=None, offset=0):
        """
        Retrieves the targets for the given joins
        """
        if len(joins) == 0:
            raise ValueError

        aggregations = []
        conditions = []
        models = []
        picks = []
        for join in joins:
            models.append(self.source_models[join['table']])
            if 'conditions' in join:
                conditions.append(join)

            if 'aggregation' in join:
                aggregations.append(join)

            if 'picks' in join:
                picks.append(join)

        query = models[0]
        if picks == []:
            query = query.select(*models)
        for pick in picks:
            query = self._apply_pick(query, pick)

        joins.pop(0)
        for join in joins:
            query = self._apply_join(query, join, models)

        for condition in conditions:
            query = self._apply_condition(query, condition)

        for aggregation in aggregations:
            query = self._apply_aggregation(query, aggregation)

        if limit:
            query = query.limit(limit).offset(offset)
        self.logger.log('get-targets', query)
        self.logger.log('get-targets-count', query.count())
        return query.execute()
