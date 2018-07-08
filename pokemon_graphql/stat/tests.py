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

class StatTests(django.test.TestCase, APIData):

    def test_nodes(self):
        stat = self.setup_stat_data(name='base stt')
        stat_name = self.setup_stat_name_data(stat, name='base stt name')
        client = Client(schema)

        id = get_id("Stat", stat.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Stat {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": stat.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("StatName", stat_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on StatName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": stat_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        stat = self.setup_stat_data(name='base stt')
        stat_name = self.setup_stat_name_data(stat, name='base stt name')

        increase_move = self.setup_move_data(name="incrs mv for base stt")
        increase_move_stat_change = self.setup_move_stat_change_data(
            move=increase_move, stat=stat, change=2
        )
        decrease_move = self.setup_move_data(name="dcrs mv for base stt")
        decrease_move_stat_change = self.setup_move_stat_change_data(
            move=decrease_move, stat=stat, change=(-2)
        )

        increase_nature = self.setup_nature_data(
            name="incrs ntr for base stt", increased_stat=stat
        )
        decrease_nature = self.setup_nature_data(
            name="dcrs ntr for base stt", decreased_stat=stat
        )
        characteristic = self.setup_characteristic_data(stat=stat)

        client = Client(schema)
        executed = client.execute('''
            query {
                stats(name: "%s") {
                    id name
                    names {id text}
                    gameIndex
                    isBattleOnly
                    increaseMoves: affectingMoves(where: {change_gt: 0}, first: 10)  {
                        edges {
                            change
                            node {id name}
                        }
                    }
                    decreaseMoves: affectingMoves(where: {change_lt: 0}, first: 10)  {
                        edges {
                            change
                            node {id name}
                        }
                    }
                    characteristics {id geneModulo}
                    moveDamageClass{id name}
                    positiveAffectingNatures {id name}
                    negativeAffectingNatures {id name}
                }
            }
        ''' % stat.name, **args)
        expected = {
            "data": {
                "stats": [
                    {
                        "id": get_id("Stat", stat.id),
                        "name": stat.name,
                        "names": [
                            {
                                "id": get_id("StatName", stat_name.id),
                                "text": stat_name.name
                            }
                        ],
                        "gameIndex": stat.game_index,
                        "isBattleOnly": stat.is_battle_only,
                        "increaseMoves": {
                            "edges": [
                                {
                                    "change": increase_move_stat_change.change,
                                    "node": {
                                        "id": get_id("Move", increase_move.id),
                                        "name": increase_move.name,
                                    }
                                }
                            ]
                        },
                        "decreaseMoves": {
                            "edges": [
                                {
                                    "change": decrease_move_stat_change.change,
                                    "node": {
                                        "id": get_id("Move", decrease_move.id),
                                        "name": decrease_move.name,
                                    }
                                }
                            ]
                        },
                        "characteristics": [
                            {
                                "id": get_id("Characteristic", characteristic.id),
                                "geneModulo": characteristic.gene_mod_5
                            }
                        ],
                        "moveDamageClass": {
                            "id": get_id("MoveDamageClass", stat.move_damage_class.id),
                            "name": stat.move_damage_class.name,
                        },
                        "positiveAffectingNatures": [
                            {
                                "id": get_id("Nature", increase_nature.id),
                                "name": increase_nature.name,
                            }
                        ],
                        "negativeAffectingNatures": [
                            {
                                "id": get_id("Nature", decrease_nature.id),
                                "name": decrease_nature.name,
                            }
                        ],
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
