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

class ContestTypeTests(django.test.TestCase, APIData):

    def test_nodes(self):
        contest_type = self.setup_contest_type_data(name='base cntst tp')
        contest_type_name = self.setup_contest_type_name_data(
            contest_type, name='base cntst tp name'
        )
        client = Client(schema)

        id = get_id("ContestType", contest_type.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ContestType {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": contest_type.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ContestTypeName", contest_type_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ContestTypeName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": contest_type_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        contest_type = self.setup_contest_type_data(name='base cntst tp')
        contest_type_name = self.setup_contest_type_name_data(
            contest_type, name='base cntst tp name')
        berry_flavor = self.setup_berry_flavor_data(
            name="bry for base cntst tp", contest_type=contest_type)

        client = Client(schema)
        executed = client.execute('''
            query {
                contestTypes(name: "%s") {
                    id name
                    names {id text}
                    berryFlavor {id name}
                }
            }
        ''' % contest_type.name, **args)
        expected = {
            "data": {
                "contestTypes": [
                    {
                        "id": get_id("ContestType", contest_type.id),
                        "name": contest_type.name,
                        "names": [
                            {
                                "id": get_id("ContestTypeName", contest_type_name.id),
                                "text": contest_type_name.name
                            }
                        ],
                        "berryFlavor": {
                            "id": get_id("BerryFlavor", berry_flavor.id),
                            "name": berry_flavor.name
                        }
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
