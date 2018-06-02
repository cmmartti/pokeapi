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

class EncounterTests(django.test.TestCase, APIData):

    def test_node(self):
        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")
        location_area_name = self.setup_location_area_name_data(
            location_area, name='base lctn area name')

        encounter_method = self.setup_encounter_method_data()
        pokemon_species = self.setup_pokemon_species_data(name='spcs for pkmn')
        pokemon = self.setup_pokemon_data(
            name='pkmn for base encntr', pokemon_species=pokemon_species)

        encounter_slot = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter = self.setup_encounter_data(
            pokemon=pokemon, location_area=location_area,
            encounter_slot=encounter_slot, min_level=30, max_level=35)

        client = Client(schema)

        id = get_id("Encounter", encounter.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Encounter {id}}}'% id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    # def test_query(self):

    #     # client = Client(schema)
    #     # executed = client.execute(
    #     #     '''
    #     #     query {
    #     #         encounters(first: 1, where: {name: "base encntr"}) {
    #     #             edges {
    #     #                 node {

    #     #                 }
    #     #             }
    #     #         }
    #     #     }
    #     #     ''',
    #     #     **args
    #     # )
    #     executed = {}
    #     expected = {
    #         "data": {
    #             "encounters": {
    #                 "edges": [
    #                     {
    #                         "node": {

    #                         }
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    #     self.assertEqual(executed, expected)
