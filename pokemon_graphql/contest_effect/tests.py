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

class ContestEffectTests(django.test.TestCase, APIData):

    def test_nodes(self):
        contest_effect = self.setup_contest_effect_data(appeal=10, jam=20)
        contest_effect_flavor_text = self.setup_contest_effect_flavor_text_data(
            contest_effect, flavor_text='base cntst efct flvr txt'
        )
        contest_effect_effect_text = self.setup_contest_effect_effect_text_data(
            contest_effect, effect='base cntst efct eftc txt'
        )
        client = Client(schema)

        id = get_id("ContestEffect", contest_effect.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ContestEffect {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        id = get_id("ContestEffectEffectText", contest_effect_effect_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ContestEffectEffectText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": contest_effect_effect_text.effect
        }}}
        self.assertEqual(executed, expected)

        id = get_id("ContestEffectFlavorText", contest_effect_flavor_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ContestEffectFlavorText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": contest_effect_flavor_text.flavor_text
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        contest_effect = self.setup_contest_effect_data(appeal=10, jam=20)
        contest_effect_flavor_text = self.setup_contest_effect_flavor_text_data(
            contest_effect, flavor_text='base cntst efct flvr txt'
        )
        contest_effect_effect_text = self.setup_contest_effect_effect_text_data(
            contest_effect, effect='base cntst efct eftc txt'
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                contestEffects(id: %s) {
                    id appeal jam
                    effectEntries {id text}
                    flavorTextEntries {id text}
                }
            }
        ''' % contest_effect.id, **args)
        expected = {
            "data": {
                "contestEffects": [
                    {
                        "id": get_id("ContestEffect", contest_effect.id),
                        "appeal": contest_effect.appeal,
                        "jam": contest_effect.jam,
                        "effectEntries": [
                            {
                                "id": get_id(
                                    "ContestEffectEffectText",
                                    contest_effect_effect_text.id
                                ),
                                "text": contest_effect_effect_text.effect
                            }
                        ],
                        "flavorTextEntries": [
                            {
                                "id": get_id(
                                    "ContestEffectFlavorText",
                                    contest_effect_flavor_text.id
                                ),
                                "text": contest_effect_flavor_text.flavor_text
                            }
                        ],
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
