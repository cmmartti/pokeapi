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

class CharacteristicTests(django.test.TestCase, APIData):

    def test_node(self):
        characteristic = self.setup_characteristic_data(gene_mod_5=5)
        characteristic_description = self.setup_characteristic_description_data(
            characteristic, description='base char desc'
        )
        client = Client(schema)

        # ---
        id = get_id("Characteristic", characteristic.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Characteristic {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("CharacteristicDescription", characteristic_description.id)
        executed = client.execute(
            '''
            query {node(id: "%s") {...on CharacteristicDescription {id text}}}
            '''
             % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": characteristic_description.description
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        stat = self.setup_stat_data(name='stt for char')
        characteristic = self.setup_characteristic_data(gene_mod_5=5, stat=stat)
        characteristic_description = self.setup_characteristic_description_data(
            characteristic, description='base char desc'
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                characteristics(first: 1) {
                    edges {node {
                            id
                            descriptions {id text}
                            geneModulo
                            highestStat {id name}
                            possibleValues
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "characteristics": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Characteristic", characteristic.id),
                                "descriptions": [
                                    {
                                        "id": get_id(
                                            "CharacteristicDescription",
                                            characteristic_description.id
                                        ),
                                        "text": characteristic_description.description,
                                    }
                                ],
                                "geneModulo": characteristic.gene_mod_5,
                                "highestStat": {
                                    "id": get_id("Stat", stat.id),
                                    "name": stat.name,
                                },
                                "possibleValues": [5, 10, 15, 20, 25, 30]
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
