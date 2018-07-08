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

class BerryFirmnessTests(django.test.TestCase, APIData):

    def test_nodes(self):
        berry_firmness = self.setup_berry_firmness_data(name='base bry frmns')
        berry_firmness_name = self.setup_berry_firmness_name_data(
            berry_firmness, name='base bry frmns nm')

        client = Client(schema)

        id = get_id("BerryFirmness", berry_firmness.id)
        executed = client.execute(
            'query {node(id: "%s") {...on BerryFirmness {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": berry_firmness.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("BerryFirmnessName", berry_firmness_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on BerryFirmnessName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": berry_firmness_name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        berry_firmness = self.setup_berry_firmness_data(name='base bry frmns')
        berry_firmness_name = self.setup_berry_firmness_name_data(
            berry_firmness, name='base bry frmns nm')
        berry = self.setup_berry_data(berry_firmness=berry_firmness, name='bry for base frmns')

        client = Client(schema)
        executed = client.execute('''
            query {
                berryFirmnesses(name: "%s") {
                    id name
                    names {id text}
                    berries {id name}
                }
            }
        ''' % berry_firmness.name, **args)
        expected = {
            "data": {
                "berryFirmnesses": [
                    {
                        "id": get_id("BerryFirmness", berry_firmness.id),
                        "name": berry_firmness.name,
                        "names": [
                            {
                                "id": get_id("BerryFirmnessName", berry_firmness_name.id),
                                "text": berry_firmness_name.name
                            }
                        ],
                        "berries": [
                            {
                                "id": get_id("Berry", berry.item.id),
                                "name": berry.item.name
                            }
                        ]
                    }
                ]
            }
        }
        from ..util_for_tests import to_dict, to_unicode
        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)
