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

class ItemCategoryTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item_category = self.setup_item_category_data(name='base itm ctgry')
        item_category_name = self.setup_item_category_name_data(
            item_category, name='base itm ctgry nm')

        client = Client(schema)

        id = get_id("ItemCategory", item_category.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemCategory {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": item_category.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ItemCategoryName", item_category_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemCategoryName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_category_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        item_category = self.setup_item_category_data(name='base itm ctgry')
        item_category_name = self.setup_item_category_name_data(
            item_category, name='base itm ctgry nm')
        item = self.setup_item_data(item_category=item_category, name='itm fr base itm ctgry')

        client = Client(schema)
        executed = client.execute('''
            query {
                itemCategories(name: "%s") {
                    id name
                    names {id text}
                    items(first: 10) {edges {node {
                        ...on Node {id}
                        name
                    }}}
                    pocket {id name}
                }
            }
        ''' % item_category.name, **args)
        expected = {
            "data": {
                "itemCategories": [
                    {
                        "id": get_id("ItemCategory", item_category.id),
                        "name": item_category.name,
                        "names": [
                            {
                                "id": get_id(
                                    "ItemCategoryName", item_category_name.id
                                ),
                                "text": item_category_name.name,
                            }
                        ],
                        "items": {
                            "edges": [
                                {
                                    "node": {
                                        "id": get_id("Item", item.id),
                                        "name": item.name,
                                    }
                                }
                            ]
                        },
                        "pocket": {
                            "id": get_id("ItemPocket", item_category.item_pocket.id),
                            "name": item_category.item_pocket.name,
                        },
                    }
                ]
            }
        }
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
