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

class TypeTests(django.test.TestCase, APIData):

    def test_node(self):
        type = self.setup_type_data(name='base tp')
        type_name = self.setup_type_name_data(type, name='base tp nm')
        type_game_index = self.setup_type_game_index_data(type, game_index=10)

        client = Client(schema)

        # ---
        id = get_id("Type", type.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Type {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": type.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("TypeName", type_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on TypeName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": type_name.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("TypeGameIndex", type_game_index.id)
        executed = client.execute(
            'query {node(id: "%s") {...on TypeGameIndex {id gameIndex}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "gameIndex": type_game_index.game_index
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        type = self.setup_type_data(name='base tp')
        type_name = self.setup_type_name_data(type, name='base tp nm')
        type_game_index = self.setup_type_game_index_data(type, game_index=10)
        move = self.setup_move_data(name="mv for base tp", type=type)
        pokemon = self.setup_pokemon_data(name="pkmn for base tp")
        pokemon_type = self.setup_pokemon_type_data(pokemon=pokemon, type=type)

        no_damage_to = self.setup_type_data(name='no damage to tp')
        half_damage_to = self.setup_type_data(name='half damage to tp')
        double_damage_to = self.setup_type_data(name='double damage to tp')
        no_damage_from = self.setup_type_data(name='no damage from tp')
        half_damage_from = self.setup_type_data(name='half damage from tp')
        double_damage_from = self.setup_type_data(name='double damage from tp')

        self.setup_type_efficacy_data(
            damage_type=type, target_type=no_damage_to, damage_factor=0
        )
        self.setup_type_efficacy_data(
            damage_type=type, target_type=half_damage_to, damage_factor=50
        )
        self.setup_type_efficacy_data(
            damage_type=type, target_type=double_damage_to, damage_factor=200
        )
        self.setup_type_efficacy_data(
            damage_type=no_damage_from, target_type=type, damage_factor=0
        )
        self.setup_type_efficacy_data(
            damage_type=half_damage_from, target_type=type, damage_factor=50
        )
        self.setup_type_efficacy_data(
            damage_type=double_damage_from, target_type=type, damage_factor=200
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                types(first: 1, where: {name: "base tp"}) {
                    edges {node {
                            id name
                            names {id text}
                            gameIndices {id gameIndex}
                            generation {id name}
                            moveDamageClass {id name}
                            moves(first: 10) {
                                edges {node {
                                    id name
                                }}
                            }
                            pokemon(first: 10) {
                                edges {
                                    slot
                                    node {
                                        id name
                                    }
                                }
                            }
                            noDamageTo {id name}
                            halfDamageTo {id name}
                            doubleDamageTo {id name}
                            noDamageFrom {id name}
                            halfDamageFrom {id name}
                            doubleDamageFrom {id name}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "types": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Type", type.id),
                                "name": type.name,
                                "names": [
                                    {
                                        "id": get_id("TypeName", type_name.id),
                                        "text": type_name.name,
                                    },
                                ],
                                "gameIndices": [
                                    {
                                        "id": get_id("TypeGameIndex", type_game_index.id),
                                        "gameIndex": type_game_index.game_index,
                                    }
                                ],
                                "generation": {
                                    "id": get_id("Generation", type.generation.id),
                                    "name": type.generation.name,
                                },
                                "moveDamageClass": {
                                    "id": get_id("MoveDamageClass", type.move_damage_class.id),
                                    "name": type.move_damage_class.name,
                                },
                                "moves": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("Move", move.id),
                                                "name": move.name,
                                            }
                                        }
                                    ]
                                },
                                "pokemon": {
                                    "edges": [
                                        {
                                            "slot": pokemon_type.slot,
                                            "node": {
                                                "id": get_id("Pokemon", pokemon.id),
                                                "name": pokemon.name,
                                            }
                                        }
                                    ]
                                },
                                "noDamageTo": [
                                    {
                                        "id": get_id("Type", no_damage_to.id),
                                        "name": no_damage_to.name,
                                    }
                                ],
                                "halfDamageTo": [
                                    {
                                        "id": get_id("Type", half_damage_to.id),
                                        "name": half_damage_to.name,
                                    }
                                ],
                                "doubleDamageTo": [
                                    {
                                        "id": get_id("Type", double_damage_to.id),
                                        "name": double_damage_to.name,
                                    }
                                ],
                                "noDamageFrom": [
                                    {
                                        "id": get_id("Type", no_damage_from.id),
                                        "name": no_damage_from.name,
                                    }
                                ],
                                "halfDamageFrom": [
                                    {
                                        "id": get_id("Type", half_damage_from.id),
                                        "name": half_damage_from.name,
                                    }
                                ],
                                "doubleDamageFrom": [
                                    {
                                        "id": get_id("Type", double_damage_from.id),
                                        "name": double_damage_from.name,
                                    }
                                ],
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
