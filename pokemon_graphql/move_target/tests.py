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

class MoveTargetTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_target = self.setup_move_target_data()
        move_target_name = self.setup_move_target_name_data(
            move_target, name='base mv trgt nm'
        )
        move_target_description = self.setup_move_target_description_data(
            move_target, description='base mv trgt desc'
        )
        client = Client(schema)

        id = get_id("MoveTarget", move_target.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveTarget {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move_target.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveTargetName", move_target_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveTargetName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_target_name.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveTargetDescription", move_target_description.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveTargetDescription {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_target_description.description
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_target = self.setup_move_target_data(name='base mv trgt')
        move_target_name = self.setup_move_target_name_data(
            move_target, name='base mv trgt nm'
        )
        move_target_description = self.setup_move_target_description_data(
            move_target, description='base mv trgt desc'
        )
        move = self.setup_move_data(name='mv for base mv trgt', move_target=move_target)

        client = Client(schema)
        executed = client.execute('''
            query {
                moveTargets(name: "%s") {
                    id name
                    names {id text}
                    descriptions {id text}
                    moves(first: 1) {edges {node {
                        id name
                    }}}
                }
            }
        ''' % move_target.name, **args)
        expected = {
            "data": {
                "moveTargets": [
                    {
                        "id": get_id("MoveTarget", move_target.id),
                        "name": move_target.name,
                        "names": [
                            {
                                "id": get_id("MoveTargetName", move_target_name.id),
                                "text": move_target_name.name,
                            }
                        ],
                        "descriptions": [
                            {
                                "id": get_id(
                                    "MoveTargetDescription", move_target_description.id
                                ),
                                "text": move_target_description.description,
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
