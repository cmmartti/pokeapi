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

class VersionTests(django.test.TestCase, APIData):

    def test_node(self):
        version = self.setup_version_data()
        name = self.setup_version_name_data(version)
        client = Client(schema)

        # ---
        id = get_id("Version", version.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Version {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": version.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("VersionName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on VersionName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        version_group = self.setup_version_group_data(name="ver grp for ver")
        version = self.setup_version_data(name="base ver", version_group=version_group)
        version_name = self.setup_version_name_data(version, name="base ver name")

        client = Client(schema)
        executed = client.execute('''
            query {
                versions(first: 1, where: {name: "base ver"}) {
                    edges {node {
                            id name
                            names {id text}
                            versionGroup {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "versions": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Version", version.id),
                                "name": version.name,
                                "names": [
                                    {
                                        "id": get_id("VersionName", version_name.id),
                                        "text": version_name.name,
                                    },
                                ],
                                "versionGroup": {
                                    "id": get_id("VersionGroup", version_group.id),
                                    "name": version_group.name,
                                    "order": version_group.order,
                                },
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
