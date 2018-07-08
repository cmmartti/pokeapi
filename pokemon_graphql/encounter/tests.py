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

class EncounterTests(django.test.TestCase, APIData):

    def test_node(self):
        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")

        encounter_method = self.setup_encounter_method_data()
        pokemon_species = self.setup_pokemon_species_data(name='spcs for pkmn')
        pokemon = self.setup_pokemon_data(
            name='pkmn for base encntr', pokemon_species=pokemon_species)

        encounter_slot = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter = self.setup_encounter_data(
            pokemon=pokemon, location_area=location_area,
            encounter_slot=encounter_slot, min_level=30, max_level=35)

        client = Client(schema)

        id = get_id("Encounter", encounter.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Encounter {id}}}'% id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    def test_query(self):
        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")

        encounter_method = self.setup_encounter_method_data()
        pokemon_species = self.setup_pokemon_species_data(name='spcs for pkmn')
        pokemon = self.setup_pokemon_data(
            name='pkmn for base encntr', pokemon_species=pokemon_species)

        encounter_slot = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter = self.setup_encounter_data(
            pokemon=pokemon, location_area=location_area,
            encounter_slot=encounter_slot, min_level=30, max_level=35)

        encounter_conditions = [
            self.setup_encounter_condition_value_data(
                self.setup_encounter_condition_data(name="encntr cndtn%i" % n),
                name="encntr cndtn val%i" % n
            ) for n in range(4)
        ]
        for condition in encounter_conditions:
            self.setup_encounter_condition_value_map_data(encounter, condition)

        client = Client(schema)
        executed = client.execute(
            '''
            query {
                encounters(first: 10) {
                    edges {
                        node {
                            id chance
                            conditionValues {id name}
                            locationArea {id name}
                            maxLevel
                            method {id name}
                            minLevel
                            pokemon {id name}
                            version {id name}
                        }
                    }
                }
            }
            ''',
            **args
        )
        expected = {
            "data": {
                "encounters": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Encounter", encounter.id),
                                "chance": encounter_slot.rarity,
                                "conditionValues": [
                                    {
                                        "id": get_id("EncounterConditionValue", c.id),
                                        "name": c.name
                                    } for c in encounter_conditions
                                ],
                                "locationArea": {
                                    "id": get_id("LocationArea", location_area.id),
                                    "name": location_area.name,
                                },
                                "maxLevel": encounter.max_level,
                                "method": {
                                    "id": get_id("EncounterMethod", encounter_method.id),
                                    "name": encounter_method.name,
                                },
                                "minLevel": encounter.min_level,
                                "pokemon": {
                                    "id": get_id("Pokemon", pokemon.id),
                                    "name": pokemon.name,
                                },
                                "version": {
                                    "id": get_id("Version", encounter.version.id),
                                    "name": encounter.version.name,
                                }
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
