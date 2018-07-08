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

class EvolutionChainTests(django.test.TestCase, APIData):

    def test_nodes(self):
        evolution_chain = self.setup_evolution_chain_data()
        species = self.setup_pokemon_species_data(evolution_chain=evolution_chain)
        evolution_details = self.setup_pokemon_evolution_data(
            evolved_species=species, min_level=5
        )
        client = Client(schema)

        #---
        id = get_id("EvolutionChain", evolution_chain.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EvolutionChain {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("EvolutionDetail", evolution_details.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EvolutionDetail {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)


    def test_query(self):
        baby_trigger_item = self.setup_item_data(name="bby itm for evo chn")
        evolution_chain = self.setup_evolution_chain_data(
            baby_trigger_item=baby_trigger_item
        )

        baby = self.setup_pokemon_species_data(
            name="bby for evo chn", is_baby=True, evolution_chain=evolution_chain
        )

        basic = self.setup_pokemon_species_data(
            name="bsc for evo chn",
            evolves_from_species=baby,
            evolution_chain=evolution_chain
        )
        basic_location = self.setup_location_data(name='lctn for bsc evo chn')
        basic_evolution = self.setup_pokemon_evolution_data(
            evolved_species=basic, min_level=5, location=basic_location
        )

        stage_one = self.setup_pokemon_species_data(
            name="stg one for evo chn",
            evolves_from_species=basic,
            evolution_chain=evolution_chain
        )
        stage_one_held_item = self.setup_item_data(name='itm for stg one evo chn')
        stage_one_evolution = self.setup_pokemon_evolution_data(
            evolved_species=stage_one, min_level=18, held_item=stage_one_held_item
        )

        stage_two_first = self.setup_pokemon_species_data(
            name="stg two frst for evo chn",
            evolves_from_species=stage_one,
            evolution_chain=evolution_chain
        )
        stage_two_first_known_move = self.setup_move_data(name="mv for evo chn")
        stage_two_first_evolution = self.setup_pokemon_evolution_data(
            evolved_species=stage_two_first,
            min_level=32,
            known_move=stage_two_first_known_move
        )

        stage_two_second = self.setup_pokemon_species_data(
            name="stg two scnd for evo chn",
            evolves_from_species=stage_one,
            evolution_chain=evolution_chain
        )
        stage_two_second_party_type = self.setup_type_data(name="tp for evo chn")
        stage_two_second_evolution = self.setup_pokemon_evolution_data(
            evolved_species=stage_two_second,
            min_level=32,
            party_type=stage_two_second_party_type
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                evolutionChains(first: 1, where: {pokemonSpecies_ID: "%s"}) {
                    edges {
                        node {
                            id
                            babyTriggerItem {
                                ...on Node {id}
                                name
                            }
                            chain {
                                ...chainFields
                                evolvesTo {
                                    ...chainFields
                                    evolvesTo {
                                        ...chainFields
                                        evolvesTo {
                                            ...chainFields
                                            evolvesTo {...chainFields}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            fragment chainFields on ChainLink {
                isBaby
                species {id name}
                conditions {
                    id
                    item {
                        ...on Node {id}
                        name
                    }
                    gender {id name}
                    heldItem {
                        ...on Node {id}
                        name
                    }
                    knownMove {id name}
                    knownMoveType {id name}
                    location {id name}
                    minLevel
                    minHappiness
                    minBeauty
                    minAffection
                    needsOverworldRain
                    partySpecies {id name}
                    partySpeciesType {id name}
                    relativePhysicalStats
                    timeOfDay
                    tradeSpecies {id name}
                    trigger {id name}
                    turnUpsideDown
                }
            }
        ''' % get_id("PokemonSpecies", stage_two_second.id), **args)

        stage_two_first_result = {
            "isBaby": stage_two_first.is_baby,
            "species": {
                "id": get_id("PokemonSpecies", stage_two_first.id),
                "name": stage_two_first.name,
            },
            "conditions": [
                {
                    "id": get_id("EvolutionDetail", stage_two_first_evolution.id),
                    "item": None,
                    "gender": None,
                    "knownMove": {
                        "id": get_id("Move", stage_two_first_evolution.known_move.id),
                        "name": stage_two_first_evolution.known_move.name,
                    },
                    "knownMoveType": None,
                    "heldItem": None,
                    "location": None,
                    "minLevel": stage_two_first_evolution.min_level,
                    "minHappiness": stage_two_first_evolution.min_happiness,
                    "minBeauty": stage_two_first_evolution.min_beauty,
                    "minAffection": stage_two_first_evolution.min_affection,
                    "needsOverworldRain": stage_two_first_evolution.needs_overworld_rain,
                    "partySpecies": None,
                    "partySpeciesType": None,
                    "relativePhysicalStats": stage_two_first_evolution.relative_physical_stats,
                    "timeOfDay": stage_two_first_evolution.time_of_day,
                    "tradeSpecies": None,
                    "trigger": {
                        "id": get_id(
                            "EvolutionTrigger",
                            stage_two_first_evolution.evolution_trigger.id
                        ),
                        "name": stage_two_first_evolution.evolution_trigger.name,
                    },
                    "turnUpsideDown": stage_two_first_evolution.turn_upside_down,
                }
            ],
            "evolvesTo": []
        }
        stage_two_second_result = {
            "isBaby": stage_two_second.is_baby,
            "species": {
                "id": get_id("PokemonSpecies", stage_two_second.id),
                "name": stage_two_second.name,
            },
            "conditions": [
                {
                    "id": get_id("EvolutionDetail", stage_two_second_evolution.id),
                    "item": None,
                    "gender": None,
                    "knownMove": None,
                    "knownMoveType": None,
                    "heldItem": None,
                    "location": None,
                    "minLevel": stage_two_second_evolution.min_level,
                    "minHappiness": stage_two_second_evolution.min_happiness,
                    "minBeauty": stage_two_second_evolution.min_beauty,
                    "minAffection": stage_two_second_evolution.min_affection,
                    "needsOverworldRain": stage_two_second_evolution.needs_overworld_rain,
                    "partySpecies": None,
                    "partySpeciesType": {
                        "id": get_id("Type", stage_two_second_evolution.party_type.id),
                        "name": stage_two_second_evolution.party_type.name,
                    },
                    "relativePhysicalStats": stage_two_second_evolution.relative_physical_stats,
                    "timeOfDay": stage_two_second_evolution.time_of_day,
                    "tradeSpecies": None,
                    "trigger": {
                        "id": get_id(
                            "EvolutionTrigger",
                            stage_two_second_evolution.evolution_trigger.id
                        ),
                        "name": stage_two_second_evolution.evolution_trigger.name,
                    },
                    "turnUpsideDown": stage_two_second_evolution.turn_upside_down,
                }
            ],
            "evolvesTo": []
        }

        stage_one_result = {
            "isBaby": stage_one.is_baby,
            "species": {
                "id": get_id("PokemonSpecies", stage_one.id),
                "name": stage_one.name,
            },
            "conditions": [
                {
                    "id": get_id("EvolutionDetail", stage_one_evolution.id),
                    "item": None,
                    "gender": None,
                    "knownMove": None,
                    "knownMoveType": None,
                    "heldItem": {
                        "id": get_id("Item", stage_one_held_item.id),
                        "name": stage_one_held_item.name,
                    },
                    "location": None,
                    "minLevel": stage_one_evolution.min_level,
                    "minHappiness": stage_one_evolution.min_happiness,
                    "minBeauty": stage_one_evolution.min_beauty,
                    "minAffection": stage_one_evolution.min_affection,
                    "needsOverworldRain": stage_one_evolution.needs_overworld_rain,
                    "partySpecies": None,
                    "partySpeciesType": None,
                    "relativePhysicalStats": stage_one_evolution.relative_physical_stats,
                    "timeOfDay": stage_one_evolution.time_of_day,
                    "tradeSpecies": None,
                    "trigger": {
                        "id": get_id(
                            "EvolutionTrigger", stage_one_evolution.evolution_trigger.id
                        ),
                        "name": stage_one_evolution.evolution_trigger.name,
                    },
                    "turnUpsideDown": stage_one_evolution.turn_upside_down,
                }
            ],
            "evolvesTo": [stage_two_first_result, stage_two_second_result]
        }

        basic_result = {
            "isBaby": basic.is_baby,
            "species": {
                "id": get_id("PokemonSpecies", basic.id),
                "name": basic.name,
            },
            "conditions": [
                {
                    "id": get_id("EvolutionDetail", basic_evolution.id),
                    "item": None,
                    "gender": None,
                    "knownMove": None,
                    "knownMoveType": None,
                    "heldItem": None,
                    "location": {
                        "id": get_id("Location", basic_evolution.location.id),
                        "name": basic_evolution.location.name,
                    },
                    "minLevel": basic_evolution.min_level,
                    "minHappiness": basic_evolution.min_happiness,
                    "minBeauty": basic_evolution.min_beauty,
                    "minAffection": basic_evolution.min_affection,
                    "needsOverworldRain": basic_evolution.needs_overworld_rain,
                    "partySpecies": None,
                    "partySpeciesType": None,
                    "relativePhysicalStats": basic_evolution.relative_physical_stats,
                    "timeOfDay": basic_evolution.time_of_day,
                    "tradeSpecies": None,
                    "trigger": {
                        "id": get_id(
                            "EvolutionTrigger", basic_evolution.evolution_trigger.id
                        ),
                        "name": basic_evolution.evolution_trigger.name,
                    },
                    "turnUpsideDown": basic_evolution.turn_upside_down,
                }
            ],
            "evolvesTo": [stage_one_result]
        }

        expected = {
            "data": {
                "evolutionChains": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("EvolutionChain", evolution_chain.id),
                                "babyTriggerItem": {
                                    "id": get_id("Item", baby_trigger_item.id),
                                    "name": baby_trigger_item.name,
                                },
                                "chain": {
                                    "isBaby": baby.is_baby,
                                    "species": {
                                        "id": get_id("PokemonSpecies", baby.id),
                                        "name": baby.name,
                                    },
                                    "conditions": [],
                                    "evolvesTo": [basic_result]
                                }
                            }
                        }
                    ]
                }
            }
        }
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
