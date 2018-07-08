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

class PokeathlonStatTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokeathlon_stat = self.setup_pokeathlon_stat_data(name='base pkathln stt')
        pokeathlon_stat_name = self.setup_pokeathlon_stat_name_data(
            pokeathlon_stat, name='base pkathln stt name'
        )
        client = Client(schema)

        id = get_id("PokeathlonStat", pokeathlon_stat.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokeathlonStat {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokeathlon_stat.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokeathlonStatName", pokeathlon_stat_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokeathlonStatName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokeathlon_stat_name.name
        }}}
        self.assertEqual(executed, expected)


    def test_query(self):
        pokeathlon_stat = self.setup_pokeathlon_stat_data(name='base pkathln stt')
        pokeathlon_stat_name = self.setup_pokeathlon_stat_name_data(
            pokeathlon_stat, name='base pkathln stt name'
        )

        nature1 = self.setup_nature_data(name='ntr1')
        nature_pokeathlon_stat1 = self.setup_nature_pokeathlon_stat_data(
            nature=nature1, pokeathlon_stat=pokeathlon_stat, max_change=1
        )

        nature2 = self.setup_nature_data(name='ntr2')
        nature_pokeathlon_stat2 = self.setup_nature_pokeathlon_stat_data(
            nature=nature2, pokeathlon_stat=pokeathlon_stat, max_change=-1
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                pokeathlonStats(name: "%s") {
                    id name
                    names {id text}
                    increaseNatures: affectingNatures(where: {maxChange_gt: 0}, first: 10)  {
                        edges {
                            maxChange
                            node {id name}
                        }
                    }
                    decreaseNatures: affectingNatures(where: {maxChange_lt: 0}, first: 10)  {
                        edges {
                            maxChange
                            node {id name}
                        }
                    }
                }
            }
        ''' % pokeathlon_stat.name, **args)
        expected = {
            "data": {
                "pokeathlonStats": [
                    {
                        "id": get_id("PokeathlonStat", pokeathlon_stat.id),
                        "name": pokeathlon_stat.name,
                        "names": [
                            {
                                "id": get_id("PokeathlonStatName", pokeathlon_stat_name.id),
                                "text": pokeathlon_stat_name.name
                            }
                        ],
                        "increaseNatures": {
                            "edges": [
                                {
                                    "maxChange": nature_pokeathlon_stat1.max_change,
                                    "node": {
                                        "id": get_id("Nature", nature1.id),
                                        "name": nature1.name,
                                    }
                                }
                            ]
                        },
                        "decreaseNatures": {
                            "edges": [
                                {
                                    "maxChange": nature_pokeathlon_stat2.max_change,
                                    "node": {
                                        "id": get_id("Nature", nature2.id),
                                        "name": nature2.name,
                                    }
                                }
                            ]
                        },
                    }
                ]
            }
        }
        self.assertEqual(executed, expected)
