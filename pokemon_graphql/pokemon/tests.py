# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
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

class PokemonTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokemon_species = self.setup_pokemon_species_data(name='pkmn spcs for base pkmn')
        pokemon = self.setup_pokemon_data(pokemon_species=pokemon_species, name='base pkm')
        pokemon_form = self.setup_pokemon_form_data(pokemon=pokemon, name='pkm form for base pkmn')
        pokemon_ability = self.setup_pokemon_ability_data(pokemon=pokemon)
        pokemon_stat = self.setup_pokemon_stat_data(pokemon=pokemon)
        pokemon_type = self.setup_pokemon_type_data(pokemon=pokemon)
        pokemon_item = self.setup_pokemon_item_data(pokemon=pokemon)
        pokemon_sprites = self.setup_pokemon_sprites_data(pokemon=pokemon)
        sprites_data = json.loads(pokemon_sprites.sprites)
        pokemon_game_index = self.setup_pokemon_game_index_data(pokemon=pokemon, game_index=10)

        move = self.setup_move_data(name='mv for pkmn')
        version_group = self.setup_version_group_data(name='ver grp '+str(move)+' for pkmn')
        pokemon_move = self.setup_pokemon_move_data(
            pokemon=pokemon, move=move, version_group=version_group, level=1
        )

        client = Client(schema)

        #---
        id = get_id("Pokemon", pokemon.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Pokemon {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokemon.name
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("PokemonGameIndex", pokemon_game_index.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonGameIndex {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("PokemonSprites", pokemon_sprites.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSprites {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    def test_query(self):
        pokemon_species = self.setup_pokemon_species_data(name='pkmn spcs for base pkmn')
        pokemon = self.setup_pokemon_data(pokemon_species=pokemon_species, name='base pkm')
        pokemon_form = self.setup_pokemon_form_data(pokemon=pokemon, name='pkm form for base pkmn')
        pokemon_ability = self.setup_pokemon_ability_data(pokemon=pokemon)
        pokemon_stat = self.setup_pokemon_stat_data(pokemon=pokemon)
        pokemon_type = self.setup_pokemon_type_data(pokemon=pokemon)
        pokemon_item = self.setup_pokemon_item_data(pokemon=pokemon)
        pokemon_sprites = self.setup_pokemon_sprites_data(pokemon=pokemon)
        sprites_data = json.loads(pokemon_sprites.sprites)
        pokemon_game_index = self.setup_pokemon_game_index_data(pokemon=pokemon, game_index=10)

        pokemon_move = self.setup_move_data(name='mv for pkmn')
        pokemon_moves = []
        for move in range(0, 4):
            pokemon_moves.append(self.setup_pokemon_move_data(
                pokemon=pokemon,
                move=pokemon_move,
                version_group=self.setup_version_group_data(
                    name='ver grp ' + str(move) + ' for pkmn'
                ),
                level=move
            ))

        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')
        location_area1 = self.setup_location_area_data(name='lctn1 area for base pkmn')
        encounter_slot1 = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter1 = self.setup_encounter_data(
            location_area=location_area1, pokemon=pokemon,
            encounter_slot=encounter_slot1, min_level=30, max_level=35
        )
        location_area2 = self.setup_location_area_data(name='lctn2 area for base pkmn')
        encounter_slot2 = self.setup_encounter_slot_data(encounter_method, slot=2, rarity=40)
        encounter2 = self.setup_encounter_data(
            location_area=location_area2, pokemon=pokemon,
            encounter_slot=encounter_slot2, min_level=32, max_level=36
        )

        def get_uri(path):
            host = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/'
            if path:
                return host + path.replace('/media/', '')
            return None

        client = Client(schema)
        executed = client.execute('''
            query {
                pokemons(first: 1, where: {name: {query: "%s"}}) {
                    edges {
                        node {
                            id name
                            abilities {
                                isHidden slot
                                node {id name}
                            }
                            baseExperience
                            forms {id name}
                            gameIndices {
                                id gameIndex
                                version {id name}
                            }
                            height
                            heldItems {
                                node {
                                    ...on Node {id}
                                    name
                                }
                                versions {
                                    rarity
                                    node {id name}
                                }
                            }
                            isDefault
                            locationAreaEncounters(first: 10) {
                                edges {
                                    node {
                                        locationArea {id name}
                                        versionDetails{
                                            maxChance
                                            encounterDetails(first: 10) {
                                                edges {node {id}}
                                            }
                                            version {id name}
                                        }
                                    }
                                }
                            }
                            moves(first: 10) {
                                edges {
                                    node {id name}
                                    versionGroups {
                                        levelLearnedAt
                                        moveLearnMethod {id name}
                                        node {id name}
                                    }
                                }
                            }
                            order
                            species {id name}
                            sprites {
                                frontDefault frontShiny
                                frontFemale frontShinyFemale
                                backDefault backShiny
                                backFemale backShinyFemale
                            }
                            stats {
                                baseStat effortPoints
                                node {id name}
                            }
                            types {
                                slot
                                node {id name}
                            }
                            weight
                        }
                    }
                }
            }
        ''' % pokemon.name, **args)

        abilities = [
            {
                "isHidden": pokemon_ability.is_hidden,
                "slot": pokemon_ability.slot,
                "node": {
                    "id": get_id("Ability", pokemon_ability.ability.id),
                    "name": pokemon_ability.ability.name,
                }
            },
        ]
        forms = [
            {
                "id": get_id("PokemonForm", pokemon_form.id),
                "name": pokemon_form.name,
            }
        ]
        gameIndices = [
            {
                "id": get_id(
                    "PokemonGameIndex", pokemon_game_index.id
                ),
                "gameIndex": pokemon_game_index.game_index,
                "version": {
                    "id": get_id(
                        "Version", pokemon_game_index.version.id
                    ),
                    "name": pokemon_game_index.version.name,
                }
            }
        ]
        heldItems = [
            {
                "node": {
                    "id": get_id("Item", pokemon_item.item.id),
                    "name": pokemon_item.item.name,
                },
                "versions": [
                    {
                        "rarity": pokemon_item.rarity,
                        "node": {
                            "id": get_id("Version", pokemon_item.version.id),
                            "name": pokemon_item.version.name,
                        }
                    }
                ]
            }
        ]
        locationAreaEncounters = {
            "edges": [
                {
                    "node": {
                        "locationArea": {
                            "id": get_id("LocationArea", location_area1.id),
                            "name": location_area1.name
                        },
                        "versionDetails":
                        [
                            {
                                "maxChance": encounter_slot1.rarity,
                                "encounterDetails": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("Encounter", encounter1.id)
                                            }
                                        }
                                    ],
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
                        "locationArea": {
                            "id": get_id("LocationArea", location_area2.id),
                            "name": location_area2.name
                        },
                        "versionDetails": [
                            {
                                "maxChance": encounter_slot2.rarity,
                                "encounterDetails": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("Encounter", encounter2.id)
                                            }
                                        }
                                    ],
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
        moves = {
            "edges": [
                {
                    "node": {
                        "id": get_id("Move", pokemon_moves[0].move.id),
                        "name": pokemon_moves[0].move.name
                    },
                    "versionGroups": [
                        {
                            "levelLearnedAt": poke_move.level,
                            "moveLearnMethod": {
                                "id": get_id(
                                    "MoveLearnMethod", poke_move.move_learn_method.id
                                ),
                                "name": poke_move.move_learn_method.name
                            },
                            "node": {
                                "id": get_id(
                                    "VersionGroup", poke_move.version_group.id
                                ),
                                "name": poke_move.version_group.name
                            }
                        } for poke_move in pokemon_moves
                    ]
                }
            ]
        }
        stats = [
            {
                "baseStat": pokemon_stat.base_stat,
                "effortPoints": pokemon_stat.effort,
                "node": {
                    "id": get_id("Stat", pokemon_stat.stat.id),
                    "name": pokemon_stat.stat.name
                }
            }
        ]
        types = [
            {
                "slot": pokemon_type.slot,
                "node": {
                    "id": get_id("Type", pokemon_type.type.id),
                    "name": pokemon_type.type.name
                }
            }
        ]

        expected = {
            "data": {
                "pokemons": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Pokemon", pokemon.id),
                                "name": pokemon.name,
                                "abilities": abilities,
                                "baseExperience": pokemon.base_experience,
                                "forms": forms,
                                "gameIndices": gameIndices,
                                "height": pokemon.height,
                                "heldItems": heldItems,
                                "isDefault": pokemon.is_default,
                                "locationAreaEncounters": locationAreaEncounters,
                                "moves": moves,
                                "order": pokemon.order,
                                "species": {
                                    "id": get_id("PokemonSpecies", pokemon_species.id),
                                    "name": pokemon_species.name
                                },
                                "sprites": {
                                    "frontDefault": get_uri(sprites_data['front_default']),
                                    "frontShiny": get_uri(sprites_data['front_shiny']),
                                    "frontFemale": get_uri(sprites_data['front_female']),
                                    "frontShinyFemale": get_uri(sprites_data['front_shiny_female']),
                                    "backDefault": get_uri(sprites_data['back_default']),
                                    "backShiny": get_uri(sprites_data['back_shiny']),
                                    "backFemale": get_uri(sprites_data['back_female']),
                                    "backShinyFemale":  get_uri(sprites_data['back_shiny_female']),
                                },
                                "stats": stats,
                                "types": types,
                                "weight": pokemon.weight,
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
