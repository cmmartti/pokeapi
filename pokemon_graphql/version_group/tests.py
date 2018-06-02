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

class VersionGroupTests(django.test.TestCase, APIData):

    def test_node(self):
        version_group = self.setup_version_group_data()
        client = Client(schema)

        # ---
        id = get_id("VersionGroup", version_group.id)
        executed = client.execute(
            'query {node(id: "%s") {...on VersionGroup {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": version_group.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        generation = self.setup_generation_data(name="gen for ver grp")
        version_group = self.setup_version_group_data(name="base ver grp", generation=generation)
        move_learn_method = self.setup_move_learn_method_data(name="mv lrn mthd for ")
        self.setup_version_group_move_learn_method_data(
            version_group=version_group, move_learn_method=move_learn_method)
        region = self.setup_region_data(name="rgn for ver grp")
        version = self.setup_version_data(name="ver for base ver grp", version_group=version_group)
        self.setup_version_group_region_data(version_group=version_group, region=region)
        pokedex = self.setup_pokedex_data(name="pkdx for base ver group")
        self.setup_pokedex_version_group_data(pokedex=pokedex, version_group=version_group)

        client = Client(schema)
        executed = client.execute('''
            query {
                versionGroups(first: 1, where: {name: "base ver grp"}) {
                    edges {node {
                            id name order
                            generation {id name}
                            versions {id name}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "versionGroups": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("VersionGroup", version_group.id),
                                "name": version_group.name,
                                "order": version_group.order,
                                "generation": {
                                    "id": get_id("Generation", generation.id),
                                    "name": generation.name,
                                },
                                "versions": [
                                    {
                                        "id": get_id("Version", version.id),
                                        "name": version.name,
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
