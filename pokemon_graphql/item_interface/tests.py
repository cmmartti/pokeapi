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

class ItemInterfaceTests(django.test.TestCase, APIData):

    def test_nodes(self):
        item = self.setup_item_data(name='base itm')
        item_name = self.setup_item_name_data(item, name='base itm name')
        item_flavor_text = self.setup_item_flavor_text_data(
            item, flavor_text='base itm flvr txt'
        )
        item_effect_text = self.setup_item_effect_text_data(
            item, effect='base nrml efct', short_effect='base shrt efct'
        )
        item_game_index = self.setup_item_game_index_data(item, game_index=10)

        client = Client(schema)

        #---
        id = get_id("ItemName", item_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_name.name
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("ItemEffectText", item_effect_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemEffectText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_effect_text.effect
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("ItemFlavorText", item_flavor_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemFlavorText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": item_flavor_text.flavor_text
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("ItemGameIndex", item_game_index.id)
        executed = client.execute(
            'query {node(id: "%s") {...on ItemGameIndex {id gameIndex}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "gameIndex": item_game_index.game_index
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        # Regular Item
        item_category = self.setup_item_category_data(name='itm ctgry for base itm')
        item_fling_effect = self.setup_item_fling_effect_data(
            name='itm flng efct for base itm'
        )
        item = self.setup_item_data(item_category, item_fling_effect, name='base itm')
        item_name = self.setup_item_name_data(item, name='base itm name')
        item_flavor_text = self.setup_item_flavor_text_data(
            item, flavor_text='base itm flvr txt'
        )
        item_effect_text = self.setup_item_effect_text_data(
            item, effect='base nrml efct', short_effect='base shrt efct'
        )
        item_attribute = self.setup_item_attribute_data()
        self.setup_item_attribute_map_data(item=item, item_attribute=item_attribute)
        item_game_index = self.setup_item_game_index_data(item, game_index=10)
        item_sprites = self.setup_item_sprites_data(item)
        sprites_data = json.loads(item_sprites.sprites)
        pokemon = self.setup_pokemon_data(name='pkmn for base itm')
        pokemon_item = self.setup_pokemon_item_data(pokemon=pokemon, item=item)
        evolution_chain = self.setup_evolution_chain_data(baby_trigger_item=item)

        move = self.setup_move_data()
        version_group = self.setup_version_group_data()
        machine = self.setup_machine_data(
            item=item, move=move, version_group=version_group, machine_number=43
        )

        # Berry Item
        berry_item_category = self.setup_item_category_data(name='itm ctgry for berry itm')
        berry_item_fling_effect = self.setup_item_fling_effect_data(
            name='itm flng efct for berry itm'
        )
        berry_item = self.setup_item_data(
            berry_item_category, berry_item_fling_effect, name='berry itm'
        )
        berry_item_name = self.setup_item_name_data(berry_item, name='berry itm name')
        berry_item_flavor_text = self.setup_item_flavor_text_data(
            berry_item, flavor_text='berry itm flvr txt'
        )
        berry_item_effect_text = self.setup_item_effect_text_data(
            berry_item, effect='berry nrml efct', short_effect='berry shrt efct'
        )
        berry_item_attribute = self.setup_item_attribute_data()
        self.setup_item_attribute_map_data(
            item=berry_item, item_attribute=berry_item_attribute
        )
        berry_item_game_index = self.setup_item_game_index_data(
            berry_item, game_index=10
        )
        berry_item_sprites = self.setup_item_sprites_data(berry_item)
        berry_sprites_data = json.loads(berry_item_sprites.sprites)

        berry_type = self.setup_type_data(name="tp fr berry bry")
        berry = self.setup_berry_data(
            name='berry bry', natural_gift_type=berry_type, item=berry_item
        )
        berry_flavor = self.setup_berry_flavor_data(name='bry flvr for berry bry')
        berry_flavor_map = self.setup_berry_flavor_map_data(
            berry=berry, berry_flavor=berry_flavor
        )

        def get_uri(path):
            host = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/'
            if path:
                return host + path.replace('/media/', '')
            return None

        client = Client(schema)
        executed = client.execute('''
            query {
                items(first: 10) {
                    edges {
                        node {
                            ...on Node {id}
                            name
                            names {id text}
                            attributes {id name}
                            category {id name}
                            cost flingPower
                            flingEffect {id name}
                            effectEntries {id text}
                            flavorTextEntries {
                                id text
                                versionGroup {id name}
                            }
                            gameIndices {
                                id gameIndex
                                generation {id name}
                            }
                            sprite
                            heldByPokemon(first: 10) {
                                edges {
                                    node {id name}
                                    versions {
                                        node {id name}
                                        rarity
                                    }
                                }
                            }
                            babyTriggerFor {id}
                            machines {id}
                            ...on Berry {
                                growthTime maxHarvest naturalGiftPower
                                size smoothness soilDryness
                                firmness {id name}
                                flavors {
                                    node {id name}
                                    potency
                                }
                                naturalGiftType {id name}
                            }
                        }
                    }
                }
            }
        ''', **args)

        item_node = {
            "id": get_id("Item", item.id),
            "name": item.name,
            "names": [
                {
                    "id": get_id("ItemName", item_name.id),
                    "text": item_name.name,
                }
            ],
            "attributes": [
                {
                    "id": get_id("ItemAttribute", item_attribute.id),
                    "name": item_attribute.name,
                }
            ],
            "category": {
                "id": get_id("ItemCategory", item_category.id),
                "name": item_category.name,
            },
            "cost": item.cost,
            "flingPower": item.fling_power,
            "flingEffect": {
                "id": get_id("ItemFlingEffect", item_fling_effect.id),
                "name": item_fling_effect.name,
            },
            "effectEntries": [
                {
                    "id": get_id("ItemEffectText", item_effect_text.id),
                    "text": item_effect_text.effect,
                }
            ],
            "flavorTextEntries": [
                {
                    "id": get_id("ItemFlavorText", item_flavor_text.id),
                    "text": item_flavor_text.flavor_text,
                    "versionGroup": {
                        "id": get_id("VersionGroup", item_flavor_text.version_group.id),
                        "name": item_flavor_text.version_group.name,
                    }
                }
            ],
            "gameIndices": [
                {
                    "id": get_id("ItemGameIndex", item_game_index.id),
                    "gameIndex": item_game_index.game_index,
                    "generation": {
                        "id": get_id("Generation", item_game_index.generation.id),
                        "name": item_game_index.generation.name
                    },
                }
            ],
            "sprite": get_uri(sprites_data['default']),
            "heldByPokemon": {
                "edges": [
                    {
                        "node": {
                            "id": get_id("Pokemon", pokemon.id),
                            "name": pokemon.name,
                        },
                        "versions": [
                            {
                                "node": {
                                    "id": get_id("Version", pokemon_item.version.id),
                                    "name": pokemon_item.version.name,
                                },
                                "rarity": pokemon_item.rarity,
                            }
                        ]
                    }
                ]
            },
            "babyTriggerFor": {
                "id": get_id("EvolutionChain", evolution_chain.id)
            },
            "machines": [
                {
                    "id": get_id("Machine", machine.id)
                }
            ]
        }

        berry_node = {
            "id": get_id("Berry", berry_item.id),
            "name": berry_item.name,
            "names": [
                {
                    "id": get_id("ItemName", berry_item_name.id),
                    "text": berry_item_name.name,
                }
            ],
            "attributes": [
                {
                    "id": get_id("ItemAttribute", berry_item_attribute.id),
                    "name": berry_item_attribute.name,
                }
            ],
            "category": {
                "id": get_id("ItemCategory", berry_item_category.id),
                "name": berry_item_category.name,
            },
            "cost": berry_item.cost,
            "flingPower": berry_item.fling_power,
            "flingEffect": {
                "id": get_id("ItemFlingEffect", berry_item_fling_effect.id),
                "name": berry_item_fling_effect.name,
            },
            "effectEntries": [
                {
                    "id": get_id("ItemEffectText", berry_item_effect_text.id),
                    "text": berry_item_effect_text.effect,
                }
            ],
            "flavorTextEntries": [
                {
                    "id": get_id("ItemFlavorText", berry_item_flavor_text.id),
                    "text": berry_item_flavor_text.flavor_text,
                    "versionGroup": {
                        "id": get_id("VersionGroup", berry_item_flavor_text.version_group.id),
                        "name": berry_item_flavor_text.version_group.name,
                    }
                }
            ],
            "gameIndices": [
                {
                    "id": get_id("ItemGameIndex", berry_item_game_index.id),
                    "gameIndex": berry_item_game_index.game_index,
                    "generation": {
                        "id": get_id("Generation", berry_item_game_index.generation.id),
                        "name": berry_item_game_index.generation.name
                    },
                }
            ],
            "sprite": get_uri(berry_sprites_data['default']),
            "heldByPokemon": {
                "edges": []
            },
            "babyTriggerFor": None,
            "machines": [],
            "growthTime": berry.growth_time,
            "maxHarvest": berry.max_harvest,
            "naturalGiftPower": berry.natural_gift_power,
            "size": berry.size,
            "smoothness": berry.smoothness,
            "soilDryness": berry.soil_dryness,
            "firmness": {
                "id": get_id("BerryFirmness", berry.berry_firmness.id),
                "name": berry.berry_firmness.name,
            },
            "flavors": [
                {
                    "node": {
                        "id": get_id("BerryFlavor", berry_flavor.id),
                        "name": berry_flavor.name,
                    },
                    "potency": berry_flavor_map.potency,
                }
            ],
            "naturalGiftType": {
                "id": get_id("Type", berry.natural_gift_type.id),
                "name": berry.natural_gift_type.name,
            }
        }

        expected = {
            "data": {
                "items": {
                    "edges": [
                        {
                            "node": item_node
                        },
                        {
                            "node": berry_node
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
