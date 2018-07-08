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

class MoveTests(django.test.TestCase, APIData):

    def test_nodes(self):
        move_effect = self.setup_move_effect_data()
        move_effect_effect_text = self.setup_move_effect_effect_text_data(move_effect)
        move = self.setup_move_data(name='base mv', move_effect=move_effect)
        move_name = self.setup_move_name_data(move, name='base mv nm')
        move_meta = self.setup_move_meta_data(move)
        move_stat_change = self.setup_move_stat_change_data(move=move, change=2)
        move_change = self.setup_move_change_data(move, power=10, pp=20, accuracy=30)
        move_effect_change = self.setup_move_effect_change_data(move_effect)
        move_effect_change_effect_text = self.setup_move_effect_change_effect_text_data(
            move_effect_change=move_effect_change, effect='efct tx for mv efct chng'
        )

        after_move = self.setup_move_data(name='after mv')
        before_move = self.setup_move_data(name='before mv')

        self.setup_contest_combo_data(move, after_move)
        self.setup_contest_combo_data(before_move, move)
        self.setup_super_contest_combo_data(move, after_move)
        self.setup_super_contest_combo_data(before_move, move)
        move_flavor_text = self.setup_move_flavor_text_data(
            move, flavor_text='flvr text for move'
        )

        client = Client(schema)

        #---
        id = get_id("Move", move.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Move {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": move.name
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveName", move_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_name.name
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveFlavorText", move_flavor_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveFlavorText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_flavor_text.flavor_text
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveEffectText", move_effect_effect_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveEffectText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": move_effect_effect_text.effect
        }}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveEffectChange", move_effect_change.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveEffectChange {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveMeta", move_meta.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveMeta {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveChange", move_change.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveChange {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        #---
        id = get_id("MoveStatChange", move_stat_change.id)
        executed = client.execute(
            'query {node(id: "%s") {...on MoveStatChange {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)


    def test_query(self):
        move_effect = self.setup_move_effect_data()
        move_effect_effect_text = self.setup_move_effect_effect_text_data(move_effect)
        move = self.setup_move_data(name='base mv', move_effect=move_effect)
        move_name = self.setup_move_name_data(move, name='base mv nm')
        move_meta = self.setup_move_meta_data(move)
        move_stat_change = self.setup_move_stat_change_data(move=move, change=2)

        move_change_type = self.setup_type_data(name="tp for mv chng")
        move_change = self.setup_move_change_data(
            move, power=10, pp=20, accuracy=30, type=move_change_type
        )

        move_effect_change = self.setup_move_effect_change_data(move_effect)
        move_effect_change_effect_text = self.setup_move_effect_change_effect_text_data(
            move_effect_change=move_effect_change, effect='efct tx for mv efct chng'
        )

        after_move = self.setup_move_data(name='after mv')
        before_move = self.setup_move_data(name='before mv')

        self.setup_contest_combo_data(move, after_move)
        self.setup_contest_combo_data(before_move, move)
        self.setup_super_contest_combo_data(move, after_move)
        self.setup_super_contest_combo_data(before_move, move)
        move_flavor_text = self.setup_move_flavor_text_data(
            move, flavor_text='flvr text for move'
        )

        machines = [
            self.setup_machine_data(
                item=self.setup_item_data(name="itm for mchn %s" % n),
                move=move,
                machine_number=n
            ) for n in range(4)
        ]

        client = Client(schema)
        executed = client.execute('''
            query {
                moves(first: 1, where: {name: "%s"}) {
                    edges {
                        node {
                            id name
                            names {id text}
                            accuracy
                            contestCombos {
                                useBefore {id name}
                                useAfter {id name}
                            }
                            contestEffect {id}
                            contestType {id name}
                            damageClass {id name}
                            effectChance
                            effectChanges {
                                id
                                effectEntries {id text}
                                versionGroup {id name}
                            }
                            effectEntries {id text}
                            flavorTextEntries {
                                id text
                                versionGroup {id name}
                            }
                            generation {id name}
                            machines {id}
                            meta {
                                id
                                ailment {id name}
                                ailmentChance
                                category {id name}
                                critRate drain flinchChance healing
                                minHits maxHits minTurns maxTurns
                                statChance
                            }
                            pastValues {
                                id accuracy effectChance power pp
                                effectEntries {id text}
                                type {id name}
                                versionGroup {id name}
                            }
                            pp priority power
                            statChanges {
                                id change
                                stat {id name}
                            }
                            superContestCombos {
                                useBefore {id name}
                                useAfter {id name}
                            }
                            superContestEffect {id}
                            target {id name}
                            type {id name}
                        }
                    }
                }
            }
        ''' % move.name, **args)

        names = [
            {
                "id": get_id("MoveName", move_name.id),
                "text": move_name.name
            }
        ]
        contestCombos = {
            "useBefore": [
                {
                    "id": get_id("Move", after_move.id),
                    "name": after_move.name
                }
            ],
            "useAfter": [
                {
                    "id": get_id("Move", before_move.id),
                    "name": before_move.name
                }
            ]
        }

        effectChanges = [
            {
                "id": get_id("MoveEffectChange", move_effect_change.id),
                "effectEntries": [
                    {
                        "id": get_id(
                            "MoveEffectChangeEffectText",
                            move_effect_change_effect_text.id
                        ),
                        "text": move_effect_change_effect_text.effect
                    }
                ],
                "versionGroup": {
                    "id": get_id("VersionGroup", move_effect_change.version_group.id),
                    "name": move_effect_change.version_group.name
                }
            }
        ]
        effectEntries = [
            {
                "id": get_id("MoveEffectText", move_effect_effect_text.id),
                "text": move_effect_effect_text.effect
            }
        ]
        flavorTextEntries = [
            {
                "id": get_id("MoveFlavorText", move_flavor_text.id),
                "text": move_flavor_text.flavor_text,
                "versionGroup": {
                    "id": get_id("VersionGroup", move_flavor_text.version_group.id),
                    "name": move_flavor_text.version_group.name
                }
            }
        ]
        meta = {
            "id": get_id("MoveMeta", move_meta.id),
            "ailment": {
                "id": get_id("MoveAilment", move_meta.move_meta_ailment.id),
                "name": move_meta.move_meta_ailment.name
            },
            "ailmentChance": move_meta.ailment_chance,
            "category": {
                "id": get_id("MoveCategory", move_meta.move_meta_category.id),
                "name": move_meta.move_meta_category.name
            },
            "critRate": move_meta.crit_rate,
            "drain": move_meta.drain,
            "flinchChance": move_meta.flinch_chance,
            "healing": move_meta.healing,
            "minHits": move_meta.min_hits,
            "maxHits": move_meta.max_hits,
            "minTurns": move_meta.min_turns,
            "maxTurns": move_meta.max_turns,
            "statChance": move_meta.stat_chance
        }
        pastValues = [
            {
                "id": get_id("MoveChange", move_change.id),
                "accuracy": move_change.accuracy,
                "effectChance": move_change.move_effect_chance,
                "power": move_change.power,
                "pp": move_change.pp,
                # "effectEntries": [
                #     {
                #         "id": get_id("MoveEffectText", .id),
                #         "text": .effect
                #     }
                # ],
                "effectEntries": [],
                "type": {
                    "id": get_id("Type", move_change.type.id),
                    "name": move_change.type.name
                },
                "versionGroup": {
                    "id": get_id("VersionGroup", move_change.version_group.id),
                    "name": move_change.version_group.name
                }
            }
        ]
        statChanges = [
            {
                "id": get_id("MoveStatChange", move_stat_change.id),
                "change": move_stat_change.change,
                "stat": {
                    "id": get_id("Stat", move_stat_change.stat.id),
                    "name": move_stat_change.stat.name
                }
            }
        ]

        expected = {
            "data": {
                "moves": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Move", move.id),
                                "name": move.name,
                                "names": names,
                                "accuracy": move.accuracy,
                                "contestCombos": contestCombos,
                                "contestEffect": {
                                    "id": get_id("ContestEffect", move.contest_effect.id)
                                },
                                "contestType": {
                                    "id": get_id("ContestType", move.contest_type.id),
                                    "name": move.contest_type.name
                                },
                                "damageClass": {
                                    "id": get_id(
                                        "MoveDamageClass", move.move_damage_class.id
                                    ),
                                    "name": move.move_damage_class.name
                                },
                                "effectChance": move.move_effect_chance,
                                "effectChanges": effectChanges,
                                "effectEntries": effectEntries,
                                "flavorTextEntries": flavorTextEntries,
                                "generation": {
                                    "id": get_id("Generation", move.generation.id),
                                    "name": move.generation.name
                                },
                                "machines": [
                                    {
                                        "id": get_id("Machine", m.id),
                                    } for m in machines
                                ],
                                "meta": meta,
                                "pastValues": pastValues,
                                "pp": move.pp,
                                "priority": move.priority,
                                "power": move.power,
                                "statChanges": statChanges,
                                "superContestCombos": contestCombos,
                                "superContestEffect": {
                                    "id": get_id(
                                        "SuperContestEffect",
                                        move.super_contest_effect.id
                                    )
                                },
                                "target": {
                                    "id": get_id("MoveTarget", move.move_target.id),
                                    "name": move.move_target.name
                                },
                                "type": {
                                    "id": get_id("Type", move.type.id),
                                    "name": move.type.name
                                },
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
