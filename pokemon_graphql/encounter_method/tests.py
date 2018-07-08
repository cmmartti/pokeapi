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

class EncounterMethodTests(django.test.TestCase, APIData):

    def test_node(self):
        encounter_method = self.setup_encounter_method_data()
        encounter_method_name = self.setup_encounter_method_name_data(encounter_method)
        client = Client(schema)

        # ---
        id = get_id("EncounterMethod", encounter_method.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterMethod {id name}}}'% id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": encounter_method.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("EncounterMethodName", encounter_method_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterMethodName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": encounter_method_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        encounter_method = self.setup_encounter_method_data(name='base encntr mthd')
        encounter_method_name = self.setup_encounter_method_name_data(
            encounter_method, name='base encntr mthd name'
        )

        client = Client(schema)
        executed = client.execute(
            '''
            query {
                encounterMethods(first: 1, where: {name: "base encntr mthd"}) {
                    edges {node {
                        id name
                        names {id text}
                        order
                    }}
                }
            }
            ''',
            **args
        )
        expected = {
            "data": {
                "encounterMethods": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("EncounterMethod", encounter_method.id),
                                "name": encounter_method.name,
                                "names": [
                                    {
                                        "id": get_id("EncounterMethodName", encounter_method_name.id),
                                        "text": encounter_method_name.name,
                                    },
                                ],
                                "order": encounter_method.order,
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
