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
from .id import VersionEncounterDetailID


args = {
    "middleware": [LoaderMiddleware()],
    "context_value": Context()
}

class VersionEncounterDetailTests(django.test.TestCase, APIData):

    def test_node(self):
        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")
        location_area_name = self.setup_location_area_name_data(
            location_area, name='base lctn area name')

        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')

        pokemon_species1 = self.setup_pokemon_species_data(name='spcs for pkmn1')
        pokemon1 = self.setup_pokemon_data(
            name='pkmn1 for base encntr', pokemon_species=pokemon_species1)
        encounter_slot1 = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter1 = self.setup_encounter_data(
            pokemon=pokemon1, location_area=location_area,
            encounter_slot=encounter_slot1, min_level=30, max_level=35)

        client = Client(schema)

        id = get_id("VersionEncounterDetail",
            VersionEncounterDetailID(
                location_area.id, pokemon1.id, encounter1.version.id
            )
        )
        executed = client.execute(
            'query {node(id: "%s") {...on VersionEncounterDetail {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)
