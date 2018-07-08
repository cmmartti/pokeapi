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

class LocationTests(django.test.TestCase, APIData):

    def test_node(self):
        location = self.setup_location_data(name='lctn')
        name = self.setup_location_name_data(location)
        game_index = self.setup_location_game_index_data(location, game_index=10)
        client = Client(schema)

        # ---
        id = get_id("Location", location.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Location {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": location.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LocationName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": name.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LocationGameIndex", game_index.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationGameIndex {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    def test_query(self):
        region = self.setup_region_data(name='rgn for lctn')
        location = self.setup_location_data(name='base lctn', region=region)
        location_name = self.setup_location_name_data(location, name='base lctn name')
        location_game_index = self.setup_location_game_index_data(location, game_index=10)
        location_area = self.setup_location_area_data(location, name="lctn area for lctn")

        client = Client(schema)
        executed = client.execute('''
            query {
                locations(first: 1, where: {name: "base lctn"}) {
                    edges {node {
                            id name
                            names {id text}
                            areas {id name gameIndex}
                            region {id name }
                            gameIndices {id gameIndex}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "locations": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Location", location.id),
                                "name": location.name,
                                "names": [
                                    {
                                        "id": get_id("LocationName", location_name.id),
                                        "text": location_name.name,
                                    },
                                ],
                                "areas": [
                                    {
                                        "id": get_id("LocationArea", location_area.id),
                                        "name": location_area.name,
                                        "gameIndex": location_area.game_index
                                    },
                                ],
                                "region": {
                                    "id": get_id("Region", region.id),
                                    "name": region.name,
                                },
                                "gameIndices": [
                                    {
                                        "id": get_id("LocationGameIndex", location_game_index.id),
                                        "gameIndex": location_game_index.game_index,
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
