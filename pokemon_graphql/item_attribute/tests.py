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

class ItemAttributeTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item_attribute = self.setup_item_attribute_data(name='base itm attr')
        item_attribute_name = self.setup_item_attribute_name_data(
            item_attribute, name='base itm attr nm'
        )
        item_attribute_description = self.setup_item_attribute_description_data(
            item_attribute, description='base itm attr desc'
        )

        client = Client(schema)

        id = get_id("ItemAttribute", item_attribute.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemAttribute {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": item_attribute.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ItemAttributeName", item_attribute_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemAttributeName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_attribute_name.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ItemAttributeDescription", item_attribute_description.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemAttributeDescription {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_attribute_description.description
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        item_attribute = self.setup_item_attribute_data(name='base itm attr')
        item_attribute_name = self.setup_item_attribute_name_data(
            item_attribute, name='base itm attr nm'
        )
        item_attribute_description = self.setup_item_attribute_description_data(
            item_attribute, description='base itm attr desc'
        )
        item = self.setup_item_data(name='itm fr base itm attr')
        self.setup_item_attribute_map_data(item_attribute=item_attribute, item=item)

        client = Client(schema)
        executed = client.execute('''
            query {
                itemAttributes(name: "%s") {
                    id name
                    names {id text}
                    descriptions {id text}
                    items(first: 10) {edges {node {
                        name
                        ...on Node {id}
                    }}}
                }
            }
        ''' % item_attribute.name, **args)
        expected = {
            "data": {
                "itemAttributes": [
                    {
                        "id": get_id("ItemAttribute", item_attribute.id),
                        "name": item_attribute.name,
                        "names": [
                            {
                                "id": get_id(
                                    "ItemAttributeName", item_attribute_name.id
                                ),
                                "text": item_attribute_name.name,
                            }
                        ],
                        "descriptions": [
                            {
                                "id": get_id(
                                    "ItemAttributeDescription", item_attribute_description.id
                                ),
                                "text": item_attribute_description.description,
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
                        }
                    }
                ]
            }
        }
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
