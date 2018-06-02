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
from .id import PokemonEncounterID


args = {
    "middleware": [LoaderMiddleware()],
    "context_value": Context()
}

class PokemonEncounterTests(django.test.TestCase, APIData):

    def test_node(self):
        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")
        pokemon_species1 = self.setup_pokemon_species_data(name='spcs for pkmn1')
        pokemon1 = self.setup_pokemon_data(
            name='pkmn1 for base encntr', pokemon_species=pokemon_species1)
        client = Client(schema)

        id = get_id("PokemonEncounter", PokemonEncounterID(
            location_area.id, pokemon1.id
        ))
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonEncounter {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)
