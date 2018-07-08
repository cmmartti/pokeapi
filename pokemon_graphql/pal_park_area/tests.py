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

class PalParkTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pal_park_area = self.setup_pal_park_area_data()
        pal_park_area_name = self.setup_pal_park_area_name_data(
            pal_park_area,
            name="base pl prk area nm"
        )
        client = Client(schema)

        # ---
        id = get_id("PalParkArea", pal_park_area.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PalParkArea {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pal_park_area.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PalParkAreaName", pal_park_area_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PalParkAreaName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pal_park_area_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        pal_park_area = self.setup_pal_park_area_data(name="base pl prk area")
        pal_park_area_name = self.setup_pal_park_area_name_data(
            pal_park_area,
            name="base pl prk area nm"
        )
        pokemon_species = self.setup_pokemon_species_data(name="pkmn spcs for pl prk")
        pal_park = self.setup_pal_park_data(
            pal_park_area=pal_park_area,
            pokemon_species=pokemon_species,
            base_score=10,
            rate=20
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                palParkAreas(name: "base pl prk area") {
                    id name
                    names {id text}
                    pokemonEncounters(first: 1) {
                        edges {
                            baseScore
                            node {id name}
                            rate
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "palParkAreas": [
                    {
                        "id": get_id("PalParkArea", pal_park_area.id),
                        "name": pal_park_area.name,
                        "names": [
                            {
                                "id": get_id("PalParkAreaName", pal_park_area_name.id),
                                "text": pal_park_area_name.name,
                            },
                        ],
                        "pokemonEncounters": {
                            "edges": [
                                {
                                    "baseScore": pal_park.base_score,
                                    "node": {
                                        "id": get_id("PokemonSpecies", pokemon_species.id),
                                        "name": pokemon_species.name,
                                    },
                                    "rate": pal_park.rate
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
