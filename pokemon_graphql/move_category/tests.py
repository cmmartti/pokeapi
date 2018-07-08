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

class MoveCategoryTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_category = self.setup_move_category_data(name='base mv ctgry')
        move_category_description = self.setup_move_category_description_data(
            move_category, description='base mv ctgry description'
        )
        client = Client(schema)

        id = get_id("MoveCategory", move_category.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveCategory {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move_category.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveCategoryDescription", move_category_description.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveCategoryDescription {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_category_description.description
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_category = self.setup_move_category_data(name='base mv ctgry')
        move_category_description = self.setup_move_category_description_data(
            move_category, description='base mv ctgry description'
        )
        move = self.setup_move_data(name='mv for base mv ctgry')
        self.setup_move_meta_data(move=move, move_category=move_category)

        client = Client(schema)
        executed = client.execute('''
            query {
                moveCategories(name: "%s") {
                    id name
                    descriptions {id text}
                    moves(first: 1) {edges {node {
                        id name
                    }}}
                }
            }
        ''' % move_category.name, **args)
        expected = {
            "data": {
                "moveCategories": [
                    {
                        "id": get_id("MoveCategory", move_category.id),
                        "name": move_category.name,
                        "descriptions": [
                            {
                                "id": get_id(
                                    "MoveCategoryDescription", move_category_description.id
                                ),
                                "text": move_category_description.description,
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
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
