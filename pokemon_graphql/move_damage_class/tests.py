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

class MoveDamageClassTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_damage_class = self.setup_move_damage_class_data(name='base mv dmg cls')
        move_damage_class_name = self.setup_move_damage_class_name_data(
            move_damage_class, name='base mv dmg cls nm'
        )
        move_damage_class_description = self.setup_move_damage_class_description_data(
            move_damage_class, description='base mv dmg cls desc'
        )
        client = Client(schema)

        id = get_id("MoveDamageClass", move_damage_class.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveDamageClass {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move_damage_class.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveDamageClassName", move_damage_class_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveDamageClassName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_damage_class_name.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveDamageClassDescription", move_damage_class_description.id)
        executed = client.execute(
            '''
            query {node(id: "%s") {
                ...on MoveDamageClassDescription {id text}
            }}
            ''' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_damage_class_description.description
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_damage_class = self.setup_move_damage_class_data(name='base mv dmg cls')
        move_damage_class_name = self.setup_move_damage_class_name_data(
            move_damage_class, name='base mv dmg cls nm'
        )
        move_damage_class_description = self.setup_move_damage_class_description_data(
            move_damage_class, description='base mv dmg cls desc'
        )
        move = self.setup_move_data(
            name='mv for base mv dmg cls', move_damage_class=move_damage_class
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                moveDamageClasses(name: "%s") {
                    id name
                    names {id text}
                    descriptions {id text}
                    moves(first: 1) {edges {node {
                        id name
                    }}}
                }
            }
        ''' % move_damage_class.name, **args)
        expected = {
            "data": {
                "moveDamageClasses": [
                    {
                        "id": get_id("MoveDamageClass", move_damage_class.id),
                        "name": move_damage_class.name,
                        "names": [
                            {
                                "id": get_id("MoveDamageClassName", move_damage_class_name.id),
                                "text": move_damage_class_name.name,
                            }
                        ],
                        "descriptions": [
                            {
                                "id": get_id("MoveDamageClassDescription", move_damage_class_description.id),
                                "text": move_damage_class_description.description,
                            }
                        ],
                        "moves": {
                            "edges": [
                                {
                                    "node": {
                                        "id": get_id("Move", move.id),
                                        "name": move.name,
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
