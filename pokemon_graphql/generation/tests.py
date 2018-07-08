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

class GenerationTests(django.test.TestCase, APIData):

    def test_node(self):
        generation = self.setup_generation_data()
        name = self.setup_generation_name_data(generation)
        client = Client(schema)

        # ---
        id = get_id("Generation", generation.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Generation {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": generation.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("GenerationName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on GenerationName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        region = self.setup_region_data(name="reg for gen")
        generation = self.setup_generation_data(name="base gen", region=region)
        generation_name = self.setup_generation_name_data(generation, name="base gen name")
        ability = self.setup_ability_data(name="ablty for base gen", generation=generation)
        move = self.setup_move_data(name="mv for base gen", generation=generation)
        pokemon_species = self.setup_pokemon_species_data(
            name="pkmn spcs for base gen", generation=generation)
        type = self.setup_type_data(name="tp for base gen", generation=generation)
        version_group = self.setup_version_group_data(
            name="ver grp for base gen", generation=generation)

        client = Client(schema)
        executed = client.execute('''
            query {
                generations(first: 1, where: {name: "base gen"}) {
                    edges {node {
                            id name
                            names {id text}
                            abilities(first: 1) {edges {node {
                                id name isMainSeries
                            }}}
                            mainRegion {id name}
                            moves(first: 10) {edges {node {
                                id name
                            }}}
                            pokemonSpecies(first: 1) {edges {node {
                                id name
                            }}}
                            types {id name}
                            versionGroups {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "generations": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Generation", generation.id),
                                "name": generation.name,
                                "names": [
                                    {
                                        "id": get_id("GenerationName", generation_name.id),
                                        "text": generation_name.name,
                                    },
                                ],
                                "abilities": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("Ability", ability.id),
                                                "name": ability.name,
                                                "isMainSeries": ability.is_main_series,
                                            }
                                        }
                                    ]
                                },
                                "mainRegion": {
                                    "id": get_id("Region", region.id),
                                    "name": region.name
                                },
                                "moves": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("Move", move.id),
                                                "name": move.name,
                                            }
                                        }
                                    ]
                                },
                                "pokemonSpecies": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("PokemonSpecies", pokemon_species.id),
                                                "name": pokemon_species.name,
                                            }
                                        }
                                    ]
                                },
                                "types": [
                                    {
                                        "id": get_id("Type", type.id),
                                        "name": type.name,
                                    }
                                ],
                                "versionGroups": [
                                    {
                                        "id": get_id("VersionGroup", version_group.id),
                                        "name": version_group.name,
                                        "order": version_group.order,
                                    },
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
