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

class PokemonHabitatTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokemon_habitat = self.setup_pokemon_habitat_data(name='base pkmn shp trgr')
        pokemon_habitat_name = self.setup_pokemon_habitat_name_data(
            pokemon_habitat, name='base pkmn shp name')
        client = Client(schema)

        # ---
        id = get_id("PokemonHabitat", pokemon_habitat.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonHabitat {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokemon_habitat.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokemonHabitatName", pokemon_habitat_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonHabitatName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_habitat_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        pokemon_habitat = self.setup_pokemon_habitat_data(name='base pkmn shp trgr')
        pokemon_habitat_name = self.setup_pokemon_habitat_name_data(
            pokemon_habitat, name='base pkmn shp name')
        pokemon_species = self.setup_pokemon_species_data(
            pokemon_habitat=pokemon_habitat, name='pkmn spcs for pkmn shp')

        client = Client(schema)
        executed = client.execute('''
            query {
                pokemonHabitats(name: "%s") {
                    id name
                    names {id text}
                    pokemonSpecies(first: 1) {
                        edges {
                            node {id name}
                        }
                    }
                }
            }
        ''' % pokemon_habitat.name, **args)
        expected = {
            "data": {
                "pokemonHabitats": [
                    {
                        "id": get_id("PokemonHabitat", pokemon_habitat.id),
                        "name": pokemon_habitat.name,
                        "names": [
                            {
                                "id": get_id("PokemonHabitatName", pokemon_habitat_name.id),
                                "text": pokemon_habitat_name.name,
                            },
                        ],
                        "pokemonSpecies": {
                            "edges": [
                                {
                                    "node": {
                                        "id": get_id("PokemonSpecies", pokemon_species.id),
                                        "name": pokemon_species.name,
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
