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

class ItemFlingEffectTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item_fling_effect = self.setup_item_fling_effect_data(name='base itm flng efct')
        item_fling_effect_effect_text = self.setup_item_fling_effect_effect_text_data(
            item_fling_effect, effect='base itm flng efct nm'
        )
        item = self.setup_item_data(
            item_fling_effect=item_fling_effect, name='itm fr base itm attr'
        )

        client = Client(schema)

        id = get_id("ItemFlingEffect", item_fling_effect.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemFlingEffect {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": item_fling_effect.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ItemFlingEffectEffectText", item_fling_effect_effect_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemFlingEffectEffectText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_fling_effect_effect_text.effect
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        item_fling_effect = self.setup_item_fling_effect_data(name='base itm flng efct')
        item_fling_effect_effect_text = self.setup_item_fling_effect_effect_text_data(
            item_fling_effect, effect='base itm flng efct nm'
        )
        item = self.setup_item_data(
            item_fling_effect=item_fling_effect, name='itm fr base itm attr'
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                itemFlingEffects(name: "%s") {
                    id name
                    effectEntries {id text}
                    items {
                        ...on Node {id}
                        name
                    }
                }
            }
        ''' % item_fling_effect.name, **args)
        expected = {
            "data": {
                "itemFlingEffects": [
                    {
                        "id": get_id("ItemFlingEffect", item_fling_effect.id),
                        "name": item_fling_effect.name,
                        "effectEntries": [
                            {
                                "id": get_id(
                                    "ItemFlingEffectEffectText",
                                    item_fling_effect_effect_text.id
                                ),
                                "text": item_fling_effect_effect_text.effect,
                            }
                        ],
                        "items": [
                            {
                                "id": get_id("Item", item.id),
                                "name": item.name,
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
