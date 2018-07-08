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

class PokedexTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokedex = self.setup_pokedex_data(name='base pkdx')
        pokedex_name = self.setup_pokedex_name_data(pokedex, name='base pkdx name')
        pokedex_description = self.setup_pokedex_description_data(
            pokedex, description='base pkdx desc'
        )
        client = Client(schema)

        id = get_id("Pokedex", pokedex.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Pokedex {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokedex.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokedexName", pokedex_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokedexName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokedex_name.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokedexDescription", pokedex_description.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokedexDescription {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokedex_description.description
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        pokedex = self.setup_pokedex_data(name='base pkdx')
        pokedex_name = self.setup_pokedex_name_data(pokedex, name='base pkdx name')
        pokedex_description = self.setup_pokedex_description_data(
            pokedex, description='base pkdx desc'
        )
        pokemon_species = self.setup_pokemon_species_data(name='pkmn spcs for base pkdx')
        dex_entry = self.setup_pokemon_dex_entry_data(
            pokedex=pokedex, pokemon_species=pokemon_species
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                pokedexes(first: 1, where:{name: "base pkdx"}) {
                    edges {
                        node {
                            id name isMainSeries
                            descriptions {id text}
                            names {id text}
                            pokemonEntries(first: 1) {
                                edges {
                                    entryNumber
                                    node {id name}
                                }
                            }
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "pokedexes": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Pokedex", pokedex.id),
                                "name": pokedex.name,
                                "isMainSeries": pokedex.is_main_series,
                                "descriptions": [
                                    {
                                        "id": get_id("PokedexDescription", pokedex_description.id),
                                        "text": pokedex_description.description
                                    }
                                ],
                                "names": [
                                    {
                                        "id": get_id("PokedexName", pokedex_name.id),
                                        "text": pokedex_name.name
                                    }
                                ],
                                "pokemonEntries": {
                                    "edges": [
                                        {
                                            "entryNumber": dex_entry.pokedex_number,
                                            "node": {
                                                "id": get_id("PokemonSpecies", pokemon_species.id),
                                                "name": pokemon_species.name
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
