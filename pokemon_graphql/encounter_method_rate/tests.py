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

class EncounterMethodRateTests(django.test.TestCase, APIData):

    def test_node(self):
        location_area = self.setup_location_area_data()
        name = self.setup_location_area_name_data(location_area)
        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')
        encounter_rate = self.setup_location_area_encounter_rate_data(
            location_area, encounter_method, rate=20)
        client = Client(schema)

        # ---
        id = get_id("EncounterVersionDetails", encounter_rate.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterVersionDetails {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("EncounterMethodRate", encounter_rate.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterMethodRate {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)
