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

class BerryFlavorTests(django.test.TestCase, APIData):

    def test_nodes(self):
        berry_flavor = self.setup_berry_flavor_data(name='base bry flvr')
        berry_flavor_name = self.setup_berry_flavor_name_data(
            berry_flavor, name='base bry flvr nm'
        )
        client = Client(schema)

        id = get_id("BerryFlavor", berry_flavor.id)
        executed = client.execute(
            'query {node(id: "%s") {...on BerryFlavor {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": berry_flavor.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("BerryFlavorName", berry_flavor_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on BerryFlavorName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": berry_flavor_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        berry_flavor = self.setup_berry_flavor_data(name='base bry flvr')
        berry_flavor_name = self.setup_berry_flavor_name_data(
            berry_flavor, name='base bry flvr nm'
        )
        berry = self.setup_berry_data(name='bry for base bry flvr')
        berry_flavor_map = self.setup_berry_flavor_map_data(
            berry=berry, berry_flavor=berry_flavor, potency=50
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                berryFlavors(name: "%s") {
                    id name
                    names {id text}
                    contestType {id name}
                    berries {
                        potency
                        node {
                            id name
                        }
                    }
                }
            }
        ''' % berry_flavor.name, **args)
        expected = {
            "data": {
                "berryFlavors": [
                    {
                        "id": get_id("BerryFlavor", berry_flavor.id),
                        "name": berry_flavor.name,
                        "names": [
                            {
                                "id": get_id("BerryFlavorName", berry_flavor_name.id),
                                "text": berry_flavor_name.name
                            }
                        ],
                        "contestType": {
                            "id": get_id("ContestType", berry_flavor.contest_type.id),
                            "name": berry_flavor.contest_type.name
                        },
                        "berries": [
                            {
                                "potency": berry_flavor_map.potency,
                                "node": {
                                    "id": get_id("Berry", berry.item.id),
                                    "name": berry.item.name
                                }
                            }
                        ]
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
