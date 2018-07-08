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

class MoveAilmentTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_ailment = self.setup_move_ailment_data(name='base mv almnt')
        move_ailment_name = self.setup_move_ailment_name_data(
            move_ailment, name='base mv almnt name')
        move = self.setup_move_data(name='mv for base mv almnt')
        self.setup_move_meta_data(move=move, move_ailment=move_ailment)
        client = Client(schema)

        id = get_id("MoveAilment", move_ailment.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveAilment {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move_ailment.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveAilmentName", move_ailment_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveAilmentName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_ailment_name.name
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_ailment = self.setup_move_ailment_data(name='base mv almnt')
        move_ailment_name = self.setup_move_ailment_name_data(
            move_ailment, name='base mv almnt name')
        move = self.setup_move_data(name='mv for base mv almnt')
        self.setup_move_meta_data(move=move, move_ailment=move_ailment)

        client = Client(schema)
        executed = client.execute('''
            query {
                moveAilments(name: "%s") {
                    id name
                    names {id text}
                    moves(first: 1) {edges {node {
                        id name
                    }}}
                }
            }
        ''' % move_ailment.name, **args)
        expected = {
            "data": {
                "moveAilments": [
                    {
                        "id": get_id("MoveAilment", move_ailment.id),
                        "name": move_ailment.name,
                        "names": [
                            {
                                "id": get_id("MoveAilmentName", move_ailment_name.id),
                                "text": move_ailment_name.name,
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
