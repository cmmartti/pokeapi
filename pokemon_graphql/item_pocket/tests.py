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

class ItemPocketTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item_pocket = self.setup_item_pocket_data(name='base itm pkt')
        item_pocket_name = self.setup_item_pocket_name_data(
            item_pocket, name='base itm pkt nm'
        )

        client = Client(schema)

        id = get_id("ItemPocket", item_pocket.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemPocket {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": item_pocket.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ItemPocketName", item_pocket_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemPocketName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_pocket_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        item_pocket = self.setup_item_pocket_data(name='base itm pkt')
        item_pocket_name = self.setup_item_pocket_name_data(
            item_pocket, name='base itm pkt nm'
        )
        item_category = self.setup_item_category_data(item_pocket=item_pocket)

        client = Client(schema)
        executed = client.execute('''
            query {
                itemPockets(name: "%s") {
                    id name
                    names {id text}
                    categories {id name}
                }
            }
        ''' % item_pocket.name, **args)
        expected = {
            "data": {
                "itemPockets": [
                    {
                        "id": get_id("ItemPocket", item_pocket.id),
                        "name": item_pocket.name,
                        "names": [
                            {
                                "id": get_id(
                                    "ItemPocketName", item_pocket_name.id
                                ),
                                "text": item_pocket_name.name,
                            }
                        ],
                        "categories": [
                            {
                                "id": get_id("ItemCategory", item_category.id),
                                "name": item_category.name,
                            }
                        ]
                    }
                ]
            }
        }
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
