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

class NatureTests(django.test.TestCase, APIData):

    def test_nodes(self):
        nature = self.setup_nature_data(name='base ntr')
        nature_name = self.setup_nature_name_data(nature, name='base ntr name')
        pokeathlon_stat = self.setup_pokeathlon_stat_data(name='pkeathln stt for ntr stt')
        nature_pokeathlon_stat = self.setup_nature_pokeathlon_stat_data(
            nature=nature, pokeathlon_stat=pokeathlon_stat, max_change=1
        )
        move_battle_style = self.setup_move_battle_style_data(
            name='mv btl stl for ntr stt'
        )
        nature_battle_style_preference = self.setup_nature_battle_style_preference_data(
            nature=nature, move_battle_style=move_battle_style
        )

        client = Client(schema)

        id = get_id("Nature", nature.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Nature {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": nature.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("NatureName", nature_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on NatureName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": nature_name.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("NatureStatChange", nature_pokeathlon_stat.id)
        executed = client.execute(
            'query {node(id: "%s") {...on NatureStatChange {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        id = get_id("MoveBattleStylePreference", nature_battle_style_preference.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveBattleStylePreference {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)


    def test_query(self):
        hates_flavor = self.setup_berry_flavor_data(name='hts flvr for base ntr')
        likes_flavor = self.setup_berry_flavor_data(name='lks flvr for base ntr')
        decreased_stat = self.setup_stat_data(name='dcrs stt for base ntr')
        increased_stat = self.setup_stat_data(name='ncrs stt for base ntr')
        nature = self.setup_nature_data(
            name='base ntr',
            hates_flavor=hates_flavor,
            likes_flavor=likes_flavor,
            decreased_stat=decreased_stat,
            increased_stat=increased_stat
        )
        nature_name = self.setup_nature_name_data(nature, name='base ntr name')

        pokeathlon_stat = self.setup_pokeathlon_stat_data(name='pkeathln stt for ntr stt')
        nature_pokeathlon_stat = self.setup_nature_pokeathlon_stat_data(
            nature=nature, pokeathlon_stat=pokeathlon_stat, max_change=1
        )

        move_battle_style = self.setup_move_battle_style_data(
            name='mv btl stl for ntr stt'
        )
        nature_battle_style_preference = self.setup_nature_battle_style_preference_data(
            nature=nature, move_battle_style=move_battle_style
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                natures(first: 1, where: {name: "%s"}) {
                    edges {
                        node {
                            id name
                            names {id text}
                            decreasedStat {id name}
                            increasedStat {id name}
                            hatesFlavor {id name}
                            likesFlavor {id name}
                            pokeathlonStatChanges {
                                id maxChange
                                node {id name}
                            }
                            moveBattleStylePreferences {
                                id lowHPPreference highHPPreference
                                node {id name}
                            }
                        }
                    }
                }
            }
        ''' % nature.name, **args)
        expected = {
            "data": {
                "natures": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Nature", nature.id),
                                "name": nature.name,
                                "names": [
                                    {
                                        "id": get_id("NatureName", nature_name.id),
                                        "text": nature_name.name,
                                    }
                                ],
                                "decreasedStat": {
                                    "id": get_id("Stat", decreased_stat.id),
                                    "name": decreased_stat.name,
                                },
                                "increasedStat": {
                                    "id": get_id("Stat", increased_stat.id),
                                    "name": increased_stat.name,
                                },
                                "hatesFlavor": {
                                    "id": get_id("BerryFlavor", hates_flavor.id),
                                    "name": hates_flavor.name,
                                },
                                "likesFlavor": {
                                    "id": get_id("BerryFlavor", likes_flavor.id),
                                    "name": likes_flavor.name,
                                },
                                "pokeathlonStatChanges": [
                                    {
                                        "id": get_id(
                                            "NatureStatChange",
                                            nature_pokeathlon_stat.id
                                        ),
                                        "maxChange": nature_pokeathlon_stat.max_change,
                                        "node": {
                                            "id": get_id(
                                                "PokeathlonStat", pokeathlon_stat.id
                                            ),
                                            "name": pokeathlon_stat.name,
                                        }
                                    }
                                ],
                                "moveBattleStylePreferences": [
                                    {
                                        "id": get_id(
                                            "MoveBattleStylePreference",
                                            nature_battle_style_preference.id
                                        ),
                                        "lowHPPreference": nature_battle_style_preference.low_hp_preference,
                                        "highHPPreference": nature_battle_style_preference.high_hp_preference,
                                        "node": {
                                            "id": get_id(
                                                "MoveBattleStyle", move_battle_style.id
                                            ),
                                            "name": move_battle_style.name
                                        }
                                    }
                                ]
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
