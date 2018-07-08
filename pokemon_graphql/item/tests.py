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

class ItemTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item = self.setup_item_data()
        client = Client(schema)

        id = get_id("Item", item.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Item {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": item.name
        }}}
        self.assertEqual(executed, expected)


# Refer to ..item_interface.tests for test_query
