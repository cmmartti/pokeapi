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

class MoveLearnMethodTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_learn_method = self.setup_move_learn_method_data(name='base mv lrn mthd')
        move_learn_method_name = self.setup_move_learn_method_name_data(
            move_learn_method, name='base mv lrn mthd nm'
        )
        move_learn_method_description = self.setup_move_learn_method_description_data(
            move_learn_method, description='base mv lrn mthd desc'
        )
        client = Client(schema)

        id = get_id("MoveLearnMethod", move_learn_method.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveLearnMethod {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move_learn_method.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveLearnMethodName", move_learn_method_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveLearnMethodName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_learn_method_name.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("MoveLearnMethodDescription", move_learn_method_description.id)
        executed = client.execute(
            '''
            query {node(id: "%s") {
                ...on MoveLearnMethodDescription {id text}
            }}
            ''' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_learn_method_description.description
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_learn_method = self.setup_move_learn_method_data(name='base mv lrn mthd')
        move_learn_method_name = self.setup_move_learn_method_name_data(
            move_learn_method, name='base mv lrn mthd nm'
        )
        move_learn_method_description = self.setup_move_learn_method_description_data(
            move_learn_method, description='base mv lrn mthd desc'
        )
        version_group = self.setup_version_group_data(
            name='ver grp for base mv lrn mthd'
        )
        self.setup_version_group_move_learn_method_data(
            version_group=version_group, move_learn_method=move_learn_method
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                moveLearnMethods(name: "%s") {
                    id name
                    names {id text}
                    descriptions {id text}
                    versionGroups {id name}
                }
            }
        ''' % move_learn_method.name, **args)
        expected = {
            "data": {
                "moveLearnMethods": [
                    {
                        "id": get_id("MoveLearnMethod", move_learn_method.id),
                        "name": move_learn_method.name,
                        "names": [
                            {
                                "id": get_id("MoveLearnMethodName", move_learn_method_name.id),
                                "text": move_learn_method_name.name,
                            }
                        ],
                        "descriptions": [
                            {
                                "id": get_id("MoveLearnMethodDescription", move_learn_method_description.id),
                                "text": move_learn_method_description.description,
                            }
                        ],
                        "versionGroups": [
                            {
                                "id": get_id("VersionGroup", version_group.id),
                                "name": version_group.name,
                            }
                        ]
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
