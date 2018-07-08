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

class SuperContestEffectTests(django.test.TestCase, APIData):

    def test_nodes(self):
        super_contest_effect = self.setup_super_contest_effect_data(appeal=10)
        super_contest_effect_flavor_text = self.setup_super_contest_effect_flavor_text_data(
            super_contest_effect, flavor_text='base spr cntst efct flvr txt'
        )
        move = self.setup_move_data(
            name="mv for base spr cntst efct", super_contest_effect=super_contest_effect
        )
        client = Client(schema)

        id = get_id("SuperContestEffect", super_contest_effect.id)
        executed = client.execute(
            'query {node(id: "%s") {...on SuperContestEffect {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        id = get_id("SuperContestEffectFlavorText", super_contest_effect_flavor_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on SuperContestEffectFlavorText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": super_contest_effect_flavor_text.flavor_text
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        super_contest_effect = self.setup_super_contest_effect_data(appeal=10)
        super_contest_effect_flavor_text = self.setup_super_contest_effect_flavor_text_data(
            super_contest_effect, flavor_text='base spr cntst efct flvr txt'
        )
        move = self.setup_move_data(
            name="mv for base spr cntst efct", super_contest_effect=super_contest_effect
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                superContestEffects(id: %s) {
                    id appeal
                    flavorTextEntries {id text}
                    moves {id name}
                }
            }
        ''' % super_contest_effect.id, **args)
        expected = {
            "data": {
                "superContestEffects": [
                    {
                        "id": get_id("SuperContestEffect", super_contest_effect.id),
                        "appeal": super_contest_effect.appeal,
                        "flavorTextEntries": [
                            {
                                "id": get_id(
                                    "SuperContestEffectFlavorText",
                                    super_contest_effect_flavor_text.id
                                ),
                                "text": super_contest_effect_flavor_text.flavor_text
                            }
                        ],
                        "moves": [
                            {
                                "id": get_id("Move", move.id),
                                "name": move.name
                            }
                        ]
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
