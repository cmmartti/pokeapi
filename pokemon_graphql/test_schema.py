# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base64 import b64encode
import collections
import django.test
import graphene
from graphene import Context
from graphene.test import Client
from graphql_relay import to_global_id as get_id

from .schema import schema
from .middleware import LoaderMiddleware
from pokemon_v2.tests import APIData


# Util functions for debugging failed tests
# Add the following 3 lines of code before the `assertEqual` call to ensure equal
# datatypes. Equal datatypes allow for useful diff messages.

#    self.maxDiff = None
#    expected = to_unicode(expected)
#    executed = to_unicode(to_dict(executed))

def to_dict(ordered_dict):
    """
    Recursively convert an OrderedDict to a regular dict. Not strictly necessary, but makes deciphering error messages loads easier, especially since a line-by-line comparison is shown if actual and expected values are the same type.
    """
    simple_dict = {}
    for key, value in ordered_dict.items():
        if isinstance(value, collections.OrderedDict):
            simple_dict[key] = to_dict(value)
        elif isinstance(value, list):
            simple_list = []
            for item in value:
                if isinstance(item, collections.OrderedDict):
                    simple_list.append(to_dict(item))
                else:
                    simple_list.append(item)
            simple_dict[key] = simple_list
        else:
            simple_dict[key] = value
    return simple_dict


def to_unicode(data):
    if isinstance(data, basestring):
        # return data.decode('utf8')
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(to_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(to_unicode, data))
    else:
        return data



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


    # Relay Nodes
    # These tests only test that `get_node`` Relay Node class methods return valid data.
    # They do not test the resolvers. Later tests cover those in full.

    def test_node_encounter_method(self):
        method = self.setup_encounter_method_data()
        name = self.setup_encounter_method_name_data(method)
        client = Client(schema)

        # ---
        id = get_id("EncounterMethod", method.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterMethod {id name}}}'% id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": method.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("EncounterMethod", method.id)
        executed = client.execute(
            'query {node(id: "%s") {...on EncounterMethod {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": method.name
        }}}
        self.assertEqual(executed, expected)

    def test_node_language(self):
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

    def test_node_location(self):
        location = self.setup_location_data(name='lctn')
        name = self.setup_location_name_data(location)
        game_index = self.setup_location_game_index_data(location, game_index=10)
        client = Client(schema)

        # ---
        id = get_id("Location", location.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Location {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": location.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LocationName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LocationGameIndex", game_index.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationGameIndex {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    def test_node_region(self):
        region = self.setup_region_data()
        name = self.setup_region_name_data(region)
        client = Client(schema)

        # ---
        id = get_id("Region", region.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Region {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": region.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("RegionName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on RegionName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_node_location_area(self):
        location_area = self.setup_location_area_data()
        name = self.setup_location_area_name_data(location_area)
        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')
        encounter_rate = self.setup_location_area_encounter_rate_data(
            location_area, encounter_method, rate=20)
        client = Client(schema)

        # ---
        id = get_id("LocationArea", location_area.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationArea {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": location_area.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("LocationAreaName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on LocationAreaName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

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

    def test_node_generation(self):
        generation = self.setup_generation_data()
        name = self.setup_generation_name_data(generation)
        client = Client(schema)

        # ---
        id = get_id("Generation", generation.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Generation {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": generation.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("GenerationName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on GenerationName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_node_version(self):
        version = self.setup_version_data()
        name = self.setup_version_name_data(version)
        client = Client(schema)

        # ---
        id = get_id("Version", version.id)
        executed = client.execute(
            'query {node(id: "%s") {...on Version {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": version.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("VersionName", name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on VersionName {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": name.name
        }}}
        self.assertEqual(executed, expected)

    def test_node_version_group(self):
        version_group = self.setup_version_group_data()
        client = Client(schema)

        # ---
        id = get_id("VersionGroup", version_group.id)
        executed = client.execute(
            'query {node(id: "%s") {...on VersionGroup {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": version_group.name
        }}}
        self.assertEqual(executed, expected)

    # End of Relay Node tests
    ########################


    # Encounter Method
    def test_encounter_methods(self):
        encounter_method = self.setup_encounter_method_data(name='base encntr mthd')
        encounter_method_name = self.setup_encounter_method_name_data(
            encounter_method, name='base encntr mthd name'
        )

        client = Client(schema)
        executed = client.execute(
            '''
            query {
                encounterMethods(first: 1, where: {name: "base encntr mthd"}) {
                    edges {node {
                        id name
                        names {id name}
                        order
                    }}
                }
            }
            ''',
            **args
        )
        expected = {
            "data": {
                "encounterMethods": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("EncounterMethod", encounter_method.id),
                                "name": encounter_method.name,
                                "names": [
                                    {
                                        "id": get_id("EncounterMethodName", encounter_method_name.id),
                                        "name": encounter_method_name.name,
                                    },
                                ],
                                "order": encounter_method.order,
                            }
                        }
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

    # Generation
    def test_generations(self):
        region = self.setup_region_data(name="reg for gen")
        generation = self.setup_generation_data(name="base gen", region=region)
        generation_name = self.setup_generation_name_data(generation, name="base gen name")
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
                    edges {node {
                            id name
                            names {id name}
                            mainRegion {id name}
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
                                "mainRegion": {
                                    "id": get_id("Region", region.id),
                                    "name": region.name
                                },
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
                    edges {node {
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
                    edges {node {
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
        self.assertEqual(executed, expected)

    # Location
    def test_locations(self):
        location = self.setup_location_data(name='base lctn')
        location_name = self.setup_location_name_data(location, name='base lctn name')
        location_game_index = self.setup_location_game_index_data(location, game_index=10)


                            # region {id name}
                            # areas {id name}

        client = Client(schema)
        executed = client.execute('''
            query {
                locations(first: 1, where: {name: "base lctn"}) {
                    edges {node {
                            id name
                            names {id name}
                            gameIndices {id gameIndex}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "locations": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Location", location.id),
                                "name": location.name,
                                "names": [
                                    {
                                        "id": get_id("LocationName", location_name.id),
                                        "name": location_name.name,
                                    },
                                ],
                                "gameIndices": [
                                    {
                                        "id": get_id("LocationGameIndex", location_game_index.id),
                                        "gameIndex": location_game_index.game_index,
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)

    # Location Area
    def test_location_areas(self):
        # Note that this test does not accurately test the maxChance value of
        # pokemonEncounter.versionDetails. The actual value is the sum of all rarities
        # in that version, but testing for that would make the test even more complex,
        # and I can't be bothered. The REST v2 tests don't do it right either.

        location = self.setup_location_data(name='lctn for base lctn area')
        location_area = self.setup_location_area_data(location, name="base lctn area")
        location_area_name = self.setup_location_area_name_data(
            location_area, name='base lctn area name')

        encounter_method = self.setup_encounter_method_data(name='encntr mthd for lctn area')
        location_area_encounter_rate = self.setup_location_area_encounter_rate_data(
            location_area, encounter_method, rate=20)

        pokemon_species1 = self.setup_pokemon_species_data(name='spcs for pkmn1')
        pokemon1 = self.setup_pokemon_data(
            name='pkmn1 for base encntr', pokemon_species=pokemon_species1)
        encounter_slot1 = self.setup_encounter_slot_data(encounter_method, slot=1, rarity=30)
        encounter1 = self.setup_encounter_data(
            pokemon=pokemon1, location_area=location_area,
            encounter_slot=encounter_slot1, min_level=30, max_level=35)

        pokemon_species2 = self.setup_pokemon_species_data(name='spcs for pkmn2')
        pokemon2 = self.setup_pokemon_data(
            name='pkmn2 for base encntr', pokemon_species=pokemon_species2)
        encounter_slot2 = self.setup_encounter_slot_data(encounter_method, slot=2, rarity=40)
        encounter2 = self.setup_encounter_data(
            pokemon=pokemon2, location_area=location_area,
            encounter_slot=encounter_slot2, min_level=32, max_level=36)

        client = Client(schema)
        executed = client.execute('''
            query {
                locationAreas(first: 1, where: {name: "base lctn area"}) {
                    edges {
                        node {
                            id name
                            names {id name}
                            gameIndex
                            location {id name}
                            encounterMethodRates {
                                id
                                encounterMethod {id name}
                                versionDetails {
                                    id rate
                                    version {id name}
                                }
                            }
                            pokemonEncounters(first: 2) {
                                edges {
                                    node {
                                        id pokemonId
                                        versionDetails {
                                            id maxChance
                                            encounterDetails(first: 10) {
                                                edges {
                                                    node {id}
                                                }
                                            }
                                            version {id name}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "locationAreas": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("LocationArea", location_area.id),
                                "name": location_area.name,
                                "names": [
                                    {
                                        "id": get_id("LocationAreaName", location_area_name.id),
                                        "name": location_area_name.name,
                                    },
                                ],
                                "gameIndex": location_area.game_index,
                                "location": {
                                    "id": get_id("Location", location.id),
                                    "name": location.name,
                                },
                                "encounterMethodRates": [
                                    {
                                        "id": get_id("EncounterMethodRate", location_area_encounter_rate.id),
                                        "encounterMethod": {
                                            "id": get_id("EncounterMethod", encounter_method.id),
                                            "name": encounter_method.name,
                                        },
                                        "versionDetails": [
                                            {
                                                "id": get_id("EncounterVersionDetails", location_area_encounter_rate.id),
                                                "rate": location_area_encounter_rate.rate,
                                                "version": {
                                                    "id": get_id("Version", location_area_encounter_rate.version.id),
                                                    "name": location_area_encounter_rate.version.name,
                                                },
                                            },
                                        ],
                                    },
                                ],
                                "pokemonEncounters": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": get_id(
                                                    "PokemonEncounter",
                                                    "{0}/{1}".format(location_area.id, pokemon1.id)
                                                ),
                                                "pokemonId": pokemon1.id,
                                                "versionDetails": [
                                                    {
                                                        "id": get_id(
                                                            "VersionEncounterDetail",
                                                            "{0}/{1}/{2}".format(
                                                                location_area.id,
                                                                pokemon1.id,
                                                                encounter1.version.id
                                                            )
                                                        ),
                                                        "maxChance": encounter_slot1.rarity,
                                                        "encounterDetails": {
                                                            "edges": [
                                                                {
                                                                    "node": {
                                                                        "id": get_id("Encounter", encounter1.id)
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "version": {
                                                            "id": get_id("Version", encounter1.version.id),
                                                            "name": encounter1.version.name,
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                        {
                                            "node": {
                                                "id": get_id(
                                                    "PokemonEncounter",
                                                    "{0}/{1}".format(location_area.id, pokemon2.id)
                                                ),
                                                "pokemonId": pokemon2.id,
                                                "versionDetails": [
                                                    {
                                                        "id": get_id(
                                                            "VersionEncounterDetail",
                                                            "{0}/{1}/{2}".format(
                                                                location_area.id,
                                                                pokemon2.id,
                                                                encounter2.version.id
                                                            )
                                                        ),
                                                        "maxChance": encounter_slot2.rarity,
                                                        "encounterDetails": {
                                                            "edges": [
                                                                {
                                                                    "node": {
                                                                        "id": get_id("Encounter", encounter2.id)
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "version": {
                                                            "id": get_id("Version", encounter2.version.id),
                                                            "name": encounter2.version.name,
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }

        self.maxDiff = None
        expected = to_unicode(expected)
        executed = to_unicode(to_dict(executed))
        self.assertEqual(executed, expected)


    # Region
    def test_regions(self):
        region = self.setup_region_data(name='base reg')
        region_name = self.setup_region_name_data(region, name='base reg name')
        location = self.setup_location_data(region=region, name="lctn for base rgn")
        generation = self.setup_generation_data(region=region, name="gnrtn for base rgn")
        pokedex = self.setup_pokedex_data(region=region, name="pkdx for base rgn")
        version_group = self.setup_version_group_data(name="ver grp for base rgn")
        self.setup_version_group_region_data(region=region, version_group=version_group)

        client = Client(schema)
        executed = client.execute('''
            query {
                regions(first: 1, where: {name: "base reg"}) {
                    edges {node {
                            id name
                            names {id name}
                            mainGeneration {id name mainRegion {id name}}
                            locations(
                                first: 1,
                                where: {name: "lctn for base rgn"}
                            ) {
                                edges {node {id name}}
                            }
                            versionGroups {id name order}
                        }
                    }
                }
            }
        ''', **args)
        expected = {
            "data": {
                "regions": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("Region", region.id),
                                "name": region.name,
                                "names": [
                                    {
                                        "id": get_id("RegionName", region_name.id),
                                        "name": region_name.name,
                                    },
                                ],
                                "mainGeneration": {
                                    "id": get_id("Generation", generation.id),
                                    "name": generation.name,
                                    "mainRegion": {
                                        "id": get_id("Region", region.id),
                                        "name": region.name,
                                    }
                                },
                                "locations": {
                                    "edges": [
                                        {"node": {
                                            "id": get_id("Location", location.id),
                                            "name": location.name,
                                        }},
                                    ]
                                },
                                "versionGroups": [
                                    {
                                        "id": get_id("VersionGroup", version_group.id),
                                        "name": version_group.name,
                                        "order": version_group.order,
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(executed, expected)
