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

class LocationAreaTests(django.test.TestCase, APIData):

    def test_node(self):
        location_area = self.setup_location_area_data()
        name = self.setup_location_area_name_data(location_area)
        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')
        encounter_rate = self.setup_location_area_encounter_rate_data(
            location_area, encounter_method, rate=20)
        client = Client(schema)

        # ---
        id = get_id("LocationArea", location_area.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationArea {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": location_area.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LocationAreaName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationAreaName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):

        # Note that this test does not accurately test the maxChance value of
        # pokemonEncounter.versionDetails. The actual value is the sum of all rarities
        # in that version, but testing for that would make the test even more complex,
        # and I can't be bothered. The REST v2 tests don't do it right either.

        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")
        location_area_name = self.setup_location_area_name_data(
            location_area, name='base lctn area name')

        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')
        location_area_encounter_rate = self.setup_location_area_encounter_rate_data(
            location_area, encounter_method, rate=20)

        pokemon_species1 = self.setup_pokemon_species_data(name='spcs for pkmn1')
        pokemon1 = self.setup_pokemon_data(
            name='pkmn1 for base encntr', pokemon_species=pokemon_species1)
        encounter_slot1 = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter1 = self.setup_encounter_data(
            pokemon=pokemon1, location_area=location_area,
            encounter_slot=encounter_slot1, min_level=30, max_level=35)

        pokemon_species2 = self.setup_pokemon_species_data(name='spcs for pkmn2')
        pokemon2 = self.setup_pokemon_data(
            name='pkmn2 for base encntr', pokemon_species=pokemon_species2)
        encounter_slot2 = self.setup_encounter_slot_data(encounter_method, slot=2, rarity=40)
        encounter2 = self.setup_encounter_data(
            pokemon=pokemon2, location_area=location_area,
            encounter_slot=encounter_slot2, min_level=32, max_level=36)

        client = Client(schema)
        executed = client.execute('''
            query {
                locationAreas(first: 1, where: {name: "base lctn area"}) {
                    edges {
                        node {
                            id name
                            names {id name}
                            gameIndex
                            location {id name}
                            encounterMethodRates {
                                id
                                encounterMethod {id name}
                                versionDetails {
                                    id rate
                                    version {id name}
                                }
                            }
                            pokemonEncounters(first: 2) {
                                edges {
                                    node {
                                        id pokemonId
                                        versionDetails {
                                            id maxChance
                                            encounterDetails(first: 10) {
                                                edges {
                                                    node {id}
                                                }
                                            }
                                            version {id name}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "locationAreas": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("LocationArea", location_area.id),
                                "name": location_area.name,
                                "names": [
                                    {
                                        "id": get_id("LocationAreaName", location_area_name.id),
                                        "name": location_area_name.name,
                                    },
                                ],
                                "gameIndex": location_area.game_index,
                                "location": {
                                    "id": get_id("Location", location.id),
                                    "name": location.name,
                                },
                                "encounterMethodRates": [
                                    {
                                        "id": get_id("EncounterMethodRate", location_area_encounter_rate.id),
                                        "encounterMethod": {
                                            "id": get_id("EncounterMethod", encounter_method.id),
                                            "name": encounter_method.name,
                                        },
                                        "versionDetails": [
                                            {
                                                "id": get_id("EncounterVersionDetails", location_area_encounter_rate.id),
                                                "rate": location_area_encounter_rate.rate,
                                                "version": {
                                                    "id": get_id("Version", location_area_encounter_rate.version.id),
                                                    "name": location_area_encounter_rate.version.name,
                                                },
                                            },
                                        ],
                                    },
                                ],
                                "pokemonEncounters": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id(
                                                    "PokemonEncounter",
                                                    "{0}/{1}".format(location_area.id, pokemon1.id)
                                                ),
                                                "pokemonId": pokemon1.id,
                                                "versionDetails": [
                                                    {
                                                        "id": get_id(
                                                            "VersionEncounterDetail",
                                                            "{0}/{1}/{2}".format(
                                                                location_area.id,
                                                                pokemon1.id,
                                                                encounter1.version.id
                                                            )
                                                        ),
                                                        "maxChance": encounter_slot1.rarity,
                                                        "encounterDetails": {
                                                            "edges": [
                                                                {
                                                                    "node": {
                                                                        "id": get_id("Encounter", encounter1.id)
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "version": {
                                                            "id": get_id("Version", encounter1.version.id),
                                                            "name": encounter1.version.name,
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                        {
                                            "node": {
                                                "id": get_id(
                                                    "PokemonEncounter",
                                                    "{0}/{1}".format(location_area.id, pokemon2.id)
                                                ),
                                                "pokemonId": pokemon2.id,
                                                "versionDetails": [
                                                    {
                                                        "id": get_id(
                                                            "VersionEncounterDetail",
                                                            "{0}/{1}/{2}".format(
                                                                location_area.id,
                                                                pokemon2.id,
                                                                encounter2.version.id
                                                            )
                                                        ),
                                                        "maxChance": encounter_slot2.rarity,
                                                        "encounterDetails": {
                                                            "edges": [
                                                                {
                                                                    "node": {
                                                                        "id": get_id("Encounter", encounter2.id)
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "version": {
                                                            "id": get_id("Version", encounter2.version.id),
                                                            "name": encounter2.version.name,
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }

        self.assertEqual(executed, expected)
