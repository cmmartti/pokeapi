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

class MachineTests(django.test.TestCase, APIData):

    def test_nodes(self):
        machine = self.setup_machine_data()
        client = Client(schema)

        id = get_id("Machine", machine.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Machine {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)


    def test_query(self):
        item = self.setup_item_data(name="itm for mchn")
        move = self.setup_move_data(name="mv for mchn")
        version_group = self.setup_version_group_data(name="ver grp for mchn")
        machine = self.setup_machine_data(item=item, move=move, version_group=version_group)

        client = Client(schema)
        executed = client.execute('''
            query {
                machines(first: 1) {
                    edges {
                        node {
                            id
                            item {
                                ...on Node {id}
                                name
                            }
                            move {id name}
                            versionGroup {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "machines": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Machine", machine.id),
                                "item": {
                                    "id": get_id("Item", item.id),
                                    "name": item.name,
                                },
                                "move": {
                                    "id": get_id("Move", move.id),
                                    "name": move.name,
                                },
                                "versionGroup": {
                                    "id": get_id("VersionGroup", version_group.id),
                                    "name": version_group.name,
                                    "order": version_group.order,
                                }
                            }
                        }
                    ]
                }
            }
        }
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
