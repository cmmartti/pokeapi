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

class LanguageTests(django.test.TestCase, APIData):

    def test_node(self):
        language = self.setup_language_data()
        name = self.setup_language_name_data(language)
        client = Client(schema)

        # ---
        id = get_id("Language", language.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Language {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": language.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LanguageName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LanguageName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_query(self):
        language = self.setup_language_data(name="base lang")
        language_name = self.setup_language_name_data(language, name="base lang name")

        client = Client(schema)
        executed = client.execute(
            '''
            query {
                languages(first: 1, where: {name: "base lang"}) {
                    edges {node {
                            id name official iso639 iso3166
                            names {id name}
                        }
                    }
                }
            }
            ''',
            **args
        )
        expected = {
            "data": {
                "languages": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Language", language.id),
                                "name": language.name,
                                "official": language.official,
                                "iso639": language.iso639,
                                "iso3166": language.iso3166,
                                "names": [
                                    {
                                        "id": get_id("LanguageName", language_name.id),
                                        "name": language_name.name
                                    },
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
