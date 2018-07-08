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

class BerryTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item = self.setup_item_data()
        berry = self.setup_berry_data(item=item)
        client = Client(schema)

        id = get_id("Berry", item.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Berry {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": item.name
        }}}
        self.assertEqual(executed, expected)


# For test_query, see ..item_interface.tests
