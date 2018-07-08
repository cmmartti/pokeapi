# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import django.test
import graphene
from graphene import Context
from graphene.test import Client
from graphql_relay import to_global_id as get_id

from ..schema import schema
from ..middleware import LoaderMiddleware
from pokemon_v2.tests import APIData


args = {
    "middleware": [LoaderMiddleware()],
    "context_value": Context()
}

class EncounterConditionValueTests(django.test.TestCase, APIData):

    def test_nodes(self):
        encounter_condition = self.setup_encounter_condition_data(
            name='base encntr cndtn'
        )
        encounter_condition_value = self.setup_encounter_condition_value_data(
            encounter_condition, name='encntr cndtn vlu for base encntr', is_default=True
        )
        encounter_condition_value_name = self.setup_encounter_condition_value_name_data(
            encounter_condition_value, name='base encntr cndtn vlu name'
        )

        client = Client(schema)


        # ---
        id = get_id("EncounterConditionValue", encounter_condition_value.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterConditionValue {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": encounter_condition_value.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("EncounterConditionValueName", encounter_condition_value_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterConditionValueName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": encounter_condition_value_name.name
        }}}
        self.assertEqual(executed, expected)

    # Refer to ..encounter_condition.tests for test_query
