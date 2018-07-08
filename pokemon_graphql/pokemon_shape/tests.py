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

class PokemonShapeTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokemon_shape = self.setup_pokemon_shape_data(name='base pkmn shp trgr')
        pokemon_shape_name = self.setup_pokemon_shape_name_data(
            pokemon_shape, name='base pkmn shp name')
        client = Client(schema)

        # ---
        id = get_id("PokemonShape", pokemon_shape.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonShape {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokemon_shape.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokemonShapeName", pokemon_shape_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonShapeName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_shape_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        pokemon_shape = self.setup_pokemon_shape_data(name='base pkmn shp trgr')
        pokemon_shape_name = self.setup_pokemon_shape_name_data(
            pokemon_shape, name='base pkmn shp name')
        pokemon_species = self.setup_pokemon_species_data(
            pokemon_shape=pokemon_shape, name='pkmn spcs for pkmn shp')

        client = Client(schema)
        executed = client.execute('''
            query {
                pokemonShapes(name: "%s") {
                    id name
                    names {id text}
                    pokemonSpecies(first: 1) {
                        edges {
                            node {id name}
                        }
                    }
                }
            }
        ''' % pokemon_shape.name, **args)
        expected = {
            "data": {
                "pokemonShapes": [
                    {
                        "id": get_id("PokemonShape", pokemon_shape.id),
                        "name": pokemon_shape.name,
                        "names": [
                            {
                                "id": get_id("PokemonShapeName", pokemon_shape_name.id),
                                "text": pokemon_shape_name.name,
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
