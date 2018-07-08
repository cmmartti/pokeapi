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

class GrowthRateTests(django.test.TestCase, APIData):

    def test_nodes(self):
        growth_rate = self.setup_growth_rate_data(name='base grth rt')
        growth_rate_description = self.setup_growth_rate_description_data(
            growth_rate, description='base grth rt desc'
        )
        experience = self.setup_experience_data(growth_rate)
        client = Client(schema)

        # ---
        id = get_id("GrowthRate", growth_rate.id)
        executed = client.execute(
            'query {node(id: "%s") {...on GrowthRate {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": growth_rate.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("GrowthRateDescription", growth_rate_description.id)
        executed = client.execute(
            'query {node(id: "%s") {...on GrowthRateDescription {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": growth_rate_description.description
        }}}
        self.assertEqual(executed, expected)

        id = get_id("GrowthRateExperienceLevel", experience.id)
        executed = client.execute(
            'query {node(id: "%s") {...on GrowthRateExperienceLevel {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    def test_query(self):
        growth_rate = self.setup_growth_rate_data(name='base grth rt')
        growth_rate_description = self.setup_growth_rate_description_data(
            growth_rate, description='base grth rt desc'
        )
        experience = self.setup_experience_data(growth_rate, level=10, experience=3000)
        experience43 = self.setup_experience_data(growth_rate, level=43, experience=18000)
        pokemon_species = self.setup_pokemon_species_data(
            name='pkmn spcs for grth rt', growth_rate=growth_rate
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                growthRates(name: "%s") {
                    id name
                    descriptions {id text}
                    levels {id level experience}
                    experienceFor43: experience(level: 43)
                    pokemonSpecies(first: 1) {
                        edges {
                            node {id name}
                        }
                    }
                }
            }
        ''' % growth_rate.name, **args)
        expected = {
            "data": {
                "growthRates": [
                    {
                        "id": get_id("GrowthRate", growth_rate.id),
                        "name": growth_rate.name,
                        "descriptions": [
                            {
                                "id": get_id("GrowthRateDescription", growth_rate_description.id),
                                "text": growth_rate_description.description,
                            },
                        ],
                        "levels": [
                            {
                                "id": get_id("GrowthRateExperienceLevel", experience.id),
                                "level": experience.level,
                                "experience": experience.experience,
                            },
                            {
                                "id": get_id("GrowthRateExperienceLevel", experience43.id),
                                "level": experience43.level,
                                "experience": experience43.experience,
                            },
                        ],
                        "experienceFor43": experience43.experience,
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
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
