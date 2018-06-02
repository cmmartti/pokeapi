# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base64 import b64encode
import django.test
import graphene
from graphene import Context
from graphene.test import Client
from graphql_relay import to_global_id as get_id

from .schema import schema
from .middleware import LoaderMiddleware
from pokemon_v2.tests import APIData


args = {
    "middleware": [LoaderMiddleware()],
    "context_value": Context()
}


def encode_cursor(position):
    return b64encode("|".join(position).encode('ascii')).decode('ascii')


class ConnectionTests(django.test.TestCase, APIData):

    def test_pagination(self):
        language1 = self.setup_language_data(name="lang1")
        language2 = self.setup_language_data(name="lang2")
        language3 = self.setup_language_data(name="lang3")
        language4 = self.setup_language_data(name="lang4")
        language5 = self.setup_language_data(name="lang5")
        language6 = self.setup_language_data(name="lang6")
        language7 = self.setup_language_data(name="lang7")
        language8 = self.setup_language_data(name="lang8")
        language9 = self.setup_language_data(name="lang9")

        client = Client(schema)

        # First 3 after 4
        executed = client.execute(
            '''query {languages(first: 3, after: "%s") {edges {node {id name}}}}''' % encode_cursor((str(language4.id), )),
            **args
        )
        expected = {
            "data": {
                "languages": {
                    "edges": [
                        {"node": {
                            "id": get_id("Language", language5.id),
                            "name": language5.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language6.id),
                            "name": language6.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language7.id),
                            "name": language7.name,
                        }},
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)

        # Last 2
        executed = client.execute(
            '''query {languages(last: 2) {edges {node {id name}}}}''',
            **args
        )
        expected = {
            "data": {
                "languages": {
                    "edges": [
                        {"node": {
                            "id": get_id("Language", language8.id),
                            "name": language8.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language9.id),
                            "name": language9.name,
                        }},
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)

    def test_ordering_with_pagination(self):
        language1 = self.setup_language_data(name="lang1")
        language2 = self.setup_language_data(name="lang2")
        language3 = self.setup_language_data(name="lang3")
        language4 = self.setup_language_data(name="lang4")
        language5 = self.setup_language_data(name="lang5")
        language6 = self.setup_language_data(name="lang6")
        language7 = self.setup_language_data(name="lang7")
        language8 = self.setup_language_data(name="lang8")
        language9 = self.setup_language_data(name="lang9")

        client = Client(schema)

        # First 3 after 4 ordered by name descending
        executed = client.execute(
            '''
            query {languages(
                first: 3, after: "%s", orderBy: {field: NAME, direction: DESC}
            ) {edges {node {id name}}}}
            ''' % encode_cursor((language6.name, str(language6.id) )),
            **args
        )
        expected = {
            "data": {
                "languages": {
                    "edges": [
                        {"node": {
                            "id": get_id("Language", language5.id),
                            "name": language5.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language4.id),
                            "name": language4.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language3.id),
                            "name": language3.name,
                        }},
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)

    def test_total_count(self):
        language1 = self.setup_language_data(name="lang1")
        language2 = self.setup_language_data(name="lang2")
        language3 = self.setup_language_data(name="lang3")
        language4 = self.setup_language_data(name="lang4")
        language5 = self.setup_language_data(name="lang5")
        language6 = self.setup_language_data(name="lang6")
        language7 = self.setup_language_data(name="lang7")
        language8 = self.setup_language_data(name="lang8")
        language9 = self.setup_language_data(name="lang9")

        client = Client(schema)

        # TotalCount
        executed = client.execute(
            '''
            query {languages(first: 3) {
                totalCount
                edges {node {id name}}}
            }
            ''',
            **args
        )
        expected = {
            "data": {
                "languages": {
                    "totalCount": 9,
                    "edges": [
                        {"node": {
                            "id": get_id("Language", language1.id),
                            "name": language1.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language2.id),
                            "name": language2.name,
                        }},
                        {"node": {
                            "id": get_id("Language", language3.id),
                            "name": language3.name,
                        }},
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
