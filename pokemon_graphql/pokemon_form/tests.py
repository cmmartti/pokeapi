# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
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

class PokemonFormTests(django.test.TestCase, APIData):

    def test_nodes(self):
        pokemon_species = self.setup_pokemon_species_data()
        pokemon = self.setup_pokemon_data(pokemon_species=pokemon_species)
        pokemon_form = self.setup_pokemon_form_data(pokemon=pokemon, name='pkm form for base pkmn')
        pokemon_form_name = self.setup_pokemon_form_name_data(pokemon_form)
        pokemon_form_sprites = self.setup_pokemon_form_sprites_data(pokemon_form)
        client = Client(schema)

        # ---
        id = get_id("PokemonForm", pokemon_form.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonForm {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokemon_form.name
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokemonFormName", pokemon_form_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonFormName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_form_name.pokemon_name or None
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokemonFormFormName", pokemon_form_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonFormFormName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_form_name.name or None
        }}}
        self.assertEqual(executed, expected)

        id = get_id("PokemonFormSprites", pokemon_form_sprites.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonFormSprites {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

    def test_query(self):
        pokemon_species = self.setup_pokemon_species_data()
        pokemon = self.setup_pokemon_data(pokemon_species=pokemon_species)
        pokemon_form = self.setup_pokemon_form_data(pokemon=pokemon, name='pkm form for base pkmn')
        pokemon_form_name = self.setup_pokemon_form_name_data(pokemon_form)
        pokemon_form_sprites = self.setup_pokemon_form_sprites_data(pokemon_form)

        sprites_data = json.loads(pokemon_form_sprites.sprites)


        def get_uri(path):
            host = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/'
            if path:
                return host + path.replace('/media/', '')
            return None


        client = Client(schema)
        executed = client.execute('''
            query {
                pokemonForms(first: 1, where: {name: "%s"}) {
                    edges {
                        node {
                            id name
                            names {id text}
                            formName
                            formNames {id text}
                            order formOrder isDefault isBattleOnly isMega
                            pokemon {id name}
                            sprites {frontDefault frontShiny backDefault backShiny}
                            versionGroup {id name}
                        }
                    }
                }
            }
        ''' % pokemon_form.name, **args)
        expected = {
            "data": {
                "pokemonForms": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("PokemonForm", pokemon_form.id),
                                "name": pokemon_form.name,
                                "names": [
                                    {
                                        "id": get_id("PokemonFormName", pokemon_form_name.id),
                                        "text": pokemon_form_name.pokemon_name,
                                    },
                                ],
                                "formName": pokemon_form.form_name or None,
                                "formNames": [
                                    {
                                        "id": get_id("PokemonFormFormName", pokemon_form_name.id),
                                        "text": pokemon_form_name.name,
                                    }
                                ],
                                "order": pokemon_form.order,
                                "formOrder": pokemon_form.form_order,
                                "isDefault": pokemon_form.is_default,
                                "isBattleOnly": pokemon_form.is_battle_only,
                                "isMega": pokemon_form.is_mega,
                                "pokemon": {
                                    "id": get_id("Pokemon", pokemon.id),
                                    "name": pokemon.name,
                                },
                                "sprites": {
                                    "frontDefault": get_uri(sprites_data['front_default']),
                                    "frontShiny": get_uri(sprites_data['front_shiny']),
                                    "backDefault": get_uri(sprites_data['back_default']),
                                    "backShiny": get_uri(sprites_data['back_shiny']),
                                },
                                "versionGroup": {
                                    "id": get_id("VersionGroup", pokemon_form.version_group.id),
                                    "name": pokemon_form.version_group.name,
                                },
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
