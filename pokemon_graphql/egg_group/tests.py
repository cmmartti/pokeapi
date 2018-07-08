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

class EggGroupTests(django.test.TestCase, APIData):

    def test_nodes(self):
        egg_group = self.setup_egg_group_data(name='base egg grp')
        egg_group_name = self.setup_egg_group_name_data(
            egg_group, name='base egg grp name'
        )
        client = Client(schema)

        # ---
        id = get_id("EggGroup", egg_group.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EggGroup {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": egg_group.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("EggGroupName", egg_group_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EggGroupName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": egg_group_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        egg_group = self.setup_egg_group_data(name='base egg grp')
        egg_group_name = self.setup_egg_group_name_data(
            egg_group, name='base egg grp name'
        )
        pokemon_species = self.setup_pokemon_species_data()
        self.setup_pokemon_egg_group_data(
            pokemon_species=pokemon_species, egg_group=egg_group
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                eggGroups(first: 1, where: {name: "%s"}) {
                    edges {
                        node {
                            id name
                            names {id text}
                            pokemonSpecies(first: 1) {
                                edges {
                                    node {id name}
                                }
                            }
                        }
                    }
                }
            }
        ''' % egg_group.name, **args)
        expected = {
            "data": {
                "eggGroups": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("EggGroup", egg_group.id),
                                "name": egg_group.name,
                                "names": [
                                    {
                                        "id": get_id("EggGroupName", egg_group_name.id),
                                        "text": egg_group_name.name,
                                    },
                                ],
                                "pokemonSpecies": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id("PokemonSpecies", pokemon_species.id),
                                                "name": pokemon_species.name,
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
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
