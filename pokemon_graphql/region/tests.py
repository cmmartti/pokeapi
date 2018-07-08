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

class RegionTests(django.test.TestCase, APIData):

    def test_node(self):
        region = self.setup_region_data()
        name = self.setup_region_name_data(region)
        client = Client(schema)

        # ---
        id = get_id("Region", region.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Region {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": region.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("RegionName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on RegionName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        region = self.setup_region_data(name='base reg')
        region_name = self.setup_region_name_data(region, name='base reg name')
        location = self.setup_location_data(region=region, name="lctn for base rgn")
        generation = self.setup_generation_data(region=region, name="gnrtn for base rgn")
        pokedex = self.setup_pokedex_data(region=region, name="pkdx for base rgn")
        version_group = self.setup_version_group_data(name="ver grp for base rgn")
        self.setup_version_group_region_data(region=region, version_group=version_group)

        client = Client(schema)
        executed = client.execute('''
            query {
                regions(first: 1) {
                    edges {node {
                            id name
                            names {id text}
                            mainGeneration {id name mainRegion {id name}}
                            locations(first: 10) {
                                edges {node {id name}}
                            }
                            pokedexes {id name isMainSeries}
                            versionGroups {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "regions": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Region", region.id),
                                "name": region.name,
                                "names": [
                                    {
                                        "id": get_id("RegionName", region_name.id),
                                        "text": region_name.name,
                                    },
                                ],
                                "mainGeneration": {
                                    "id": get_id("Generation", generation.id),
                                    "name": generation.name,
                                    "mainRegion": {
                                        "id": get_id("Region", region.id),
                                        "name": region.name,
                                    }
                                },
                                "locations": {
                                    "edges": [
                                        {"node": {
                                            "id": get_id("Location", location.id),
                                            "name": location.name,
                                        }},
                                    ]
                                },
                                "pokedexes": [
                                    {
                                        "id": get_id("Pokedex", pokedex.id),
                                        "name": pokedex.name,
                                        "isMainSeries": pokedex.is_main_series,
                                    }
                                ],
                                "versionGroups": [
                                    {
                                        "id": get_id("VersionGroup", version_group.id),
                                        "name": version_group.name,
                                        "order": version_group.order,
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
