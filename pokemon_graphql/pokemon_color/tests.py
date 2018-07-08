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

class PokemonColorTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokemon_color = self.setup_pokemon_color_data(name='base pkmn clr trgr')
        pokemon_color_name = self.setup_pokemon_color_name_data(
            pokemon_color, name='base pkmn clr name')
        client = Client(schema)

        # ---
        id = get_id("PokemonColor", pokemon_color.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonColor {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokemon_color.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokemonColorName", pokemon_color_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonColorName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_color_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        pokemon_color = self.setup_pokemon_color_data(name='base pkmn clr trgr')
        pokemon_color_name = self.setup_pokemon_color_name_data(
            pokemon_color, name='base pkmn clr name')
        pokemon_species = self.setup_pokemon_species_data(
            pokemon_color=pokemon_color, name='pkmn spcs for pkmn clr')

        client = Client(schema)
        executed = client.execute('''
            query {
                pokemonColors(name: "%s") {
                    id name
                    names {id text}
                    pokemonSpecies(first: 1) {
                        edges {
                            node {id name}
                        }
                    }
                }
            }
        ''' % pokemon_color.name, **args)
        expected = {
            "data": {
                "pokemonColors": [
                    {
                        "id": get_id("PokemonColor", pokemon_color.id),
                        "name": pokemon_color.name,
                        "names": [
                            {
                                "id": get_id("PokemonColorName", pokemon_color_name.id),
                                "text": pokemon_color_name.name,
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
