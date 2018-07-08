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

class AbilityTests(django.test.TestCase, APIData):

    def test_node(self):
        ability = self.setup_ability_data(name='base ablty')
        ability_name = self.setup_ability_name_data(ability, name='base ablty name')
        ability_effect_text = self.setup_ability_effect_text_data(ability, effect='base ablty efct')
        ability_flavor_text = self.setup_ability_flavor_text_data(
            ability, flavor_text='base flvr txt')
        ability_change = self.setup_ability_change_data(ability)
        ability_change_effect_text = self.setup_ability_change_effect_text_data(
            ability_change, effect='base ablty chng efct')
        pokemon = self.setup_pokemon_data(name='pkmn for ablty')
        pokemon_ability = self.setup_pokemon_ability_data(ability=ability, pokemon=pokemon)
        client = Client(schema)

        # ---
        id = get_id("Ability", ability.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Ability {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": ability.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("AbilityName", ability_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on AbilityName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": ability_name.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("AbilityEffect", ability_effect_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on AbilityEffect {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": ability_effect_text.effect
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("AbilityEffectChange", ability_change.id)
        executed = client.execute(
            'query {node(id: "%s") {...on AbilityEffectChange {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("AbilityChangeEffectText", ability_change_effect_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on AbilityChangeEffectText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": ability_change_effect_text.effect
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("AbilityFlavorText", ability_flavor_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on AbilityFlavorText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": ability_flavor_text.flavor_text
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        ability = self.setup_ability_data(name='base ablty')
        ability_name = self.setup_ability_name_data(ability, name='base ablty name')
        ability_effect_text = self.setup_ability_effect_text_data(ability, effect='base ablty efct')
        ability_flavor_text = self.setup_ability_flavor_text_data(
            ability, flavor_text='base flvr txt')
        ability_change = self.setup_ability_change_data(ability)
        ability_change_effect_text = self.setup_ability_change_effect_text_data(
            ability_change, effect='base ablty chng efct')
        pokemon = self.setup_pokemon_data(name='pkmn for ablty')
        pokemon_ability = self.setup_pokemon_ability_data(ability=ability, pokemon=pokemon)

        client = Client(schema)
        executed = client.execute('''
            query {
                abilities(first: 1) {
                    edges {node {
                            id name isMainSeries
                            names {id text}
                            generation {id name}
                            effectEntries {id text shortText}
                            effectChanges {
                                effectEntries {id text}
                                versionGroup {id name}
                            }
                            flavorTextEntries {
                                id text
                                versionGroup {id name}
                            }
                            pokemon(first: 1) {
                                edges {
                                    isHidden slot
                                    node {
                                        id name
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
                "abilities": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Ability", ability.id),
                                "name": ability.name,
                                "isMainSeries": ability.is_main_series,
                                "names": [
                                    {
                                        "id": get_id("AbilityName", ability_name.id),
                                        "text": ability_name.name,
                                    },
                                ],
                                "generation": {
                                    "id": get_id(
                                        "Generation",
                                        ability.generation.id
                                    ),
                                    "name": ability.generation.name,
                                },
                                "effectEntries": [
                                    {
                                        "id": get_id("AbilityEffect", ability_effect_text.id),
                                        "text": ability_effect_text.effect,
                                        "shortText": ability_effect_text.short_effect,
                                    }
                                ],
                                "effectChanges": [
                                    {
                                        "effectEntries": [
                                            {
                                                "id": get_id(
                                                    "AbilityChangeEffectText",
                                                    ability_change_effect_text.id
                                                ),
                                                "text": ability_change_effect_text.effect,
                                            }
                                        ],
                                        "versionGroup": {
                                            "id": get_id(
                                                "VersionGroup",
                                                ability_change.version_group.id
                                            ),
                                            "name": ability_change.version_group.name
                                        }
                                    }
                                ],
                                "flavorTextEntries": [
                                    {
                                        "id": get_id(
                                            "AbilityFlavorText",
                                            ability_flavor_text.id
                                        ),
                                        "text": ability_flavor_text.flavor_text,
                                        "versionGroup": {
                                            "id": get_id(
                                                "VersionGroup",
                                                ability_flavor_text.version_group.id
                                            ),
                                            "name": ability_flavor_text.version_group.name
                                        }
                                    }
                                ],
                                "pokemon": {
                                    "edges": [
                                        {
                                            "isHidden": pokemon_ability.is_hidden,
                                            "slot": pokemon_ability.slot,
                                            "node": {
                                                "id": get_id("Pokemon", pokemon.id),
                                                "name": pokemon.name,
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
