# -*- coding: utf-8 -*-
from base64 import b64encode
from collections import OrderedDict
import django.test
import graphene
from graphene import Context
from graphene.test import Client
from graphql_relay import to_global_id as get_id

from .schema import schema
from .middleware import LoaderMiddleware
from pokemon_v2.tests import APIData

# Util functions for tests
def to_dict(ordered_dict):
    """
    Recursively convert an OrderedDict to a regular dict. Not strictly necessary, but makes deciphering error messages loads easier, especially since a line-by-line comparison is shown if actual and expected values are the same type.
    """
    simple_dict = {}
    for key, value in ordered_dict.items():
        if isinstance(value, OrderedDict):
            simple_dict[key] = to_dict(value)
        elif isinstance(value, list):
            simple_list = []
            for item in value:
                if isinstance(item, OrderedDict):
                    simple_list.append(to_dict(item))
                else:
                    simple_list.append(item)
            simple_dict[key] = simple_list
        else:
            simple_dict[key] = value
    return simple_dict


def encode_cursor(position):
    return b64encode("|".join(position).encode('ascii')).decode('ascii')


args = {
    "middleware": [LoaderMiddleware()],
    "context_value": Context()
}


# TESTS
# In order to not go down the rabbit-hole, only test first-level resolvers in these tests, meaning don't request non-scalar fields of fields. Those are invidually tested anyway, so no point in making the tests unnecessarily complex.

class GraphQLTests(django.test.TestCase, APIData):

    # Pagination and Ordering
    def test_pagination_and_ordering(self):
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

    # Language
    def test_languages(self):
        language = self.setup_language_data(name="base lang")
        language_name = self.setup_language_name_data(language, name="base lang name")

        client = Client(schema)
        executed = client.execute(
            '''
            query {
                languages(first: 1, where: {name: "base lang"}) {
                    edges {
                        node {
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

    # Generation
    def test_generations(self):
        generation = self.setup_generation_data(name="base gen")
        generation_name = self.setup_generation_name_data(generation, name="base reg name")
        ability = self.setup_ability_data(name="ablty for base gen", generation=generation)
        move = self.setup_move_data(name="mv for base gen", generation=generation)
        pokemon_species = self.setup_pokemon_species_data(
            name="pkmn spcs for base gen", generation=generation)
        type = self.setup_type_data(name="tp for base gen", generation=generation)
        version_group = self.setup_version_group_data(
            name="ver grp for base gen", generation=generation)

        client = Client(schema)
        executed = client.execute('''
            query {
                generations(first: 1, where: {name: "base gen"}) {
                    edges {
                        node {
                            id name
                            names {id name}
                            versionGroups {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "generations": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Generation", generation.id),
                                "name": generation.name,
                                "names": [
                                    {
                                        "id": get_id("GenerationName", generation_name.id),
                                        "name": generation_name.name,
                                    },
                                ],
                                "versionGroups": [
                                    {
                                        "id": get_id("VersionGroup", version_group.id),
                                        "name": version_group.name,
                                        "order": version_group.order,
                                    },
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)

    # Version
    def test_verisons(self):
        self.maxDiff = None
        version_group = self.setup_version_group_data(name="ver grp for ver")
        version = self.setup_version_data(name="base ver", version_group=version_group)
        version_name = self.setup_version_name_data(version, name="base ver name")

        client = Client(schema)
        executed = client.execute('''
            query {
                versions(first: 1, where: {name: "base ver"}) {
                    edges {
                        node {
                            id name
                            names {id name}
                            versionGroup {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "versions": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Version", version.id),
                                "name": version.name,
                                "names": [
                                    {
                                        "id": get_id("VersionName", version_name.id),
                                        "name": version_name.name,
                                    },
                                ],
                                "versionGroup": {
                                    "id": get_id("VersionGroup", version_group.id),
                                    "name": version_group.name,
                                    "order": version_group.order,
                                },
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)

    # VersionGroup
    def test_verison_groups(self):
        generation = self.setup_generation_data(name="gen for ver grp")
        version_group = self.setup_version_group_data(name="base ver grp", generation=generation)
        move_learn_method = self.setup_move_learn_method_data(name="mv lrn mthd for ")
        self.setup_version_group_move_learn_method_data(
            version_group=version_group, move_learn_method=move_learn_method)
        region = self.setup_region_data(name="rgn for ver grp")
        version = self.setup_version_data(name="ver for base ver grp", version_group=version_group)
        self.setup_version_group_region_data(version_group=version_group, region=region)
        pokedex = self.setup_pokedex_data(name="pkdx for base ver group")
        self.setup_pokedex_version_group_data(pokedex=pokedex, version_group=version_group)

        client = Client(schema)
        executed = client.execute('''
            query {
                versionGroups(first: 1, where: {name: "base ver grp"}) {
                    edges {
                        node {
                            id name order
                            generation {id name}
                            versions {id name}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "versionGroups": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("VersionGroup", version_group.id),
                                "name": version_group.name,
                                "order": version_group.order,
                                "generation": {
                                    "id": get_id("Generation", generation.id),
                                    "name": generation.name,
                                },
                                "versions": [
                                    {
                                        "id": get_id("Version", version.id),
                                        "name": version.name,
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(to_dict(executed), expected)
