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

class GenderTests(django.test.TestCase, APIData):

    def test_nodes(self):
        gender = self.setup_gender_data(name="male")
        client = Client(schema)

        id = get_id("Gender", gender.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Gender {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": gender.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        gender = self.setup_gender_data(name='female')
        male_pokemon_species = self.setup_pokemon_species_data(
            name='ml pkmn spcs for gndr', gender_rate=8
        )
        female_pokemon_species = self.setup_pokemon_species_data(
            name='fml pkmn spcs for gndr', gender_rate=0
        )
        genderless_pokemon_species = self.setup_pokemon_species_data(
            name='gndrlss pkmn spcs for gndr', gender_rate=-1
        )
        self.setup_pokemon_evolution_data(
            evolved_species=female_pokemon_species, gender=gender
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                genders(name: "%s") {
                    id name
                    pokemonSpecies(first: 1) {
                        edges {
                            rate requiredForEvolution
                            node {id name}
                        }
                    }
                }
            }
        ''' % gender.name, **args)
        expected = {
            "data": {
                "genders": [
                    {
                        "id": get_id("Gender", gender.id),
                        "name": gender.name,
                        "pokemonSpecies": {
                            "edges": [
                                {
                                    "rate": female_pokemon_species.gender_rate,
                                    "requiredForEvolution": None,
                                    "node": {
                                        "id": get_id(
                                            "PokemonSpecies",
                                            female_pokemon_species.id
                                        ),
                                        "name": female_pokemon_species.name
                                    }
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
