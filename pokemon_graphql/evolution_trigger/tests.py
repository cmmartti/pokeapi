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

class EvolutionTriggerTests(django.test.TestCase, APIData):

    def test_nodes(self):
        evolution_trigger = self.setup_evolution_trigger_data(
            name='base evltn trgr'
        )
        evolution_trigger_name = self.setup_evolution_trigger_name_data(
            evolution_trigger, name='base evltn trgr name'
        )
        client = Client(schema)

        id = get_id("EvolutionTrigger", evolution_trigger.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EvolutionTrigger {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": evolution_trigger.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("EvolutionTriggerName", evolution_trigger_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EvolutionTriggerName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": evolution_trigger_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        evolution_trigger = self.setup_evolution_trigger_data(
            name='base evltn trgr'
        )
        evolution_trigger_name = self.setup_evolution_trigger_name_data(
            evolution_trigger, name='base evltn trgr name'
        )
        pokemon_species = self.setup_pokemon_species_data(
            name='pkmn spcs for base evltn trgr'
        )
        self.setup_pokemon_evolution_data(
            evolved_species=pokemon_species, evolution_trigger=evolution_trigger
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                evolutionTriggers(name: "%s") {
                    id name
                    names {id text}
                    pokemonSpecies(first: 10) {
                        edges {node {id name}}
                    }
                }
            }
        ''' % evolution_trigger.name, **args)
        expected = {
            "data": {
                "evolutionTriggers": [
                    {
                        "id": get_id("EvolutionTrigger", evolution_trigger.id),
                        "name": evolution_trigger.name,
                        "names": [
                            {
                                "id": get_id("EvolutionTriggerName", evolution_trigger_name.id),
                                "text": evolution_trigger_name.name
                            }
                        ],
                        "pokemonSpecies": {
                            "edges": [
                                {
                                    "node": {
                                        "id": get_id(
                                            "PokemonSpecies",
                                            pokemon_species.id
                                        ),
                                        "name": pokemon_species.name
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
