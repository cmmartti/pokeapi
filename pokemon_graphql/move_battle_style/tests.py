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

class MoveBattleStyleTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_battle_style = self.setup_move_battle_style_data(name='base mv btl stl')
        move_battle_style_name = self.setup_move_battle_style_name_data(
            move_battle_style, name='base mv btl stl name'
        )
        client = Client(schema)

        id = get_id("MoveBattleStyle", move_battle_style.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveBattleStyle {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move_battle_style.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveBattleStyleName", move_battle_style_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveBattleStyleName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_battle_style_name.name
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_battle_style = self.setup_move_battle_style_data(name='base mv btl stl')
        move_battle_style_name = self.setup_move_battle_style_name_data(
            move_battle_style, name='base mv btl stl name'
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                moveBattleStyles(name: "%s") {
                    id name
                    names {id text}
                }
            }
        ''' % move_battle_style.name, **args)
        expected = {
            "data": {
                "moveBattleStyles": [
                    {
                        "id": get_id("MoveBattleStyle", move_battle_style.id),
                        "name": move_battle_style.name,
                        "names": [
                            {
                                "id": get_id("MoveBattleStyleName", move_battle_style_name.id),
                                "text": move_battle_style_name.name,
                            }
                        ],
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
