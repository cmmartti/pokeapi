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

class PokemonSpeciesTests(django.test.TestCase, APIData):

    def test_nodes(self):
        evolves_from_species = self.setup_pokemon_species_data(
            name='evolves from pkmn spcs'
        )
        pokemon_species = self.setup_pokemon_species_data(
            evolves_from_species=evolves_from_species, name='base pkmn spcs'
        )
        pokemon_species_name = self.setup_pokemon_species_name_data(
            pokemon_species, name='base pkmn shp name'
        )
        pokemon_species_form_description = self.setup_pokemon_species_form_description_data(
            pokemon_species, description='frm dscr for pkmn spcs'
        )
        pokemon_species_flavor_text = self.setup_pokemon_species_flavor_text_data(
            pokemon_species, flavor_text='flvr txt for pkmn spcs'
        )
        pokedex = self.setup_pokedex_data(name='pkdx for pkmn spcs')
        pal_park = self.setup_pal_park_data(pokemon_species=pokemon_species)
        dex_number = self.setup_pokemon_dex_entry_data(
            pokemon_species=pokemon_species, pokedex=pokedex, entry_number=44
        )

        client = Client(schema)
        # ---
        id = get_id("PokemonSpecies", pokemon_species.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpecies {id name}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "name": pokemon_species.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PokemonSpeciesName", pokemon_species_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpeciesName {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_species_name.name
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PokemonSpeciesFlavorText", pokemon_species_flavor_text.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpeciesFlavorText {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_species_flavor_text.flavor_text
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PokemonSpeciesDescription", pokemon_species_form_description.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpeciesDescription {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_species_form_description.description
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PokemonSpeciesGenus", pokemon_species_name.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpeciesGenus {id text}}}' % id,
            **args
        )
        expected = {"data": {"node": {
            "id": id,
            "text": pokemon_species_name.genus
        }}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PokemonSpeciesPokedexEntry", dex_number.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpeciesPokedexEntry {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)

        # ---
        id = get_id("PokemonSpeciesPalParkEncounter", pal_park.id)
        executed = client.execute(
            'query {node(id: "%s") {...on PokemonSpeciesPalParkEncounter {id}}}' % id,
            **args
        )
        expected = {"data": {"node": {"id": id}}}
        self.assertEqual(executed, expected)


    def test_query(self):
        evolves_from_species = self.setup_pokemon_species_data(
            name='evolves from pkmn spcs'
        )
        evolution_chain = self.setup_evolution_chain_data()
        pokemon_species = self.setup_pokemon_species_data(
            evolves_from_species=evolves_from_species,
            name='base pkmn spcs',
            evolution_chain=evolution_chain
        )
        self.setup_pokemon_evolution_data(evolved_species=pokemon_species)

        color = pokemon_species.pokemon_color
        shape = pokemon_species.pokemon_shape
        pokemon_species_name = self.setup_pokemon_species_name_data(
            pokemon_species, name='base pkmn shp name'
        )
        pokemon_species_form_description = self.setup_pokemon_species_form_description_data(
            pokemon_species, description='frm dscr for pkmn spcs'
        )
        pokemon_species_flavor_text = self.setup_pokemon_species_flavor_text_data(
            pokemon_species, flavor_text='flvr txt for pkmn spcs'
        )
        pokedex = self.setup_pokedex_data(name='pkdx for pkmn spcs')
        pal_park = self.setup_pal_park_data(pokemon_species=pokemon_species)
        dex_number = self.setup_pokemon_dex_entry_data(
            pokemon_species=pokemon_species, pokedex=pokedex, entry_number=44
        )
        egg_group = self.setup_egg_group_data(name='egg grp for pkmn spcs')
        self.setup_pokemon_egg_group_data(
            pokemon_species=pokemon_species, egg_group=egg_group
        )
        pokemon = self.setup_pokemon_data(
            pokemon_species=pokemon_species, name='pkm for base pkmn spcs'
        )

        client = Client(schema)
        executed = client.execute('''
            query {
                pokemonSpecies(first: 1, where: {name: "%s"}) {
                    edges {
                        node {
                            id name
                            names {id text}
                            baseHappiness captureRate
                            color {id name}
                            eggGroups {id name}
                            evolutionChain {id}
                            evolvesFromSpecies {id name}
                            flavorTextEntries {id text}
                            formDescriptions {id text}
                            formsSwitchable genderRate
                            genera {id text}
                            generation {id name}
                            growthRate {id name}
                            habitat {id name}
                            hasGenderDifferences hatchCounter isBaby order
                            pokedexNumbers {
                                id entryNumber
                                node {id name}
                            }
                            shape {id name}
                            palParkEncounters {
                                id baseScore rate
                                node {id name}
                            }
                            varieties {id name}
                        }
                    }
                }
            }
        ''' % pokemon_species.name, **args)
        expected = {
            "data": {
                "pokemonSpecies": {
                    "edges": [
                        {
                            "node": {
                                "id": get_id("PokemonSpecies", pokemon_species.id),
                                "name": pokemon_species.name,
                                "names": [
                                    {
                                        "id": get_id(
                                            "PokemonSpeciesName",
                                            pokemon_species_name.id
                                        ),
                                        "text": pokemon_species_name.name,
                                    }
                                ],
                                "baseHappiness": pokemon_species.base_happiness,
                                "captureRate": pokemon_species.capture_rate,
                                "color": {
                                    "id": get_id("PokemonColor", color.id),
                                    "name": color.name,
                                },
                                "eggGroups": [
                                    {
                                        "id": get_id("EggGroup", egg_group.id),
                                        "name": egg_group.name,
                                    }
                                ],
                                "evolutionChain": {
                                    "id": get_id("EvolutionChain", evolution_chain.id)
                                },
                                "evolvesFromSpecies": {
                                    "id": get_id("PokemonSpecies", evolves_from_species.id),
                                    "name": evolves_from_species.name,
                                },
                                "flavorTextEntries": [
                                    {
                                        "id": get_id(
                                            "PokemonSpeciesFlavorText",
                                            pokemon_species_flavor_text.id
                                        ),
                                        "text": pokemon_species_flavor_text.flavor_text
                                    }
                                ],
                                "formDescriptions": [
                                    {
                                        "id": get_id(
                                            "PokemonSpeciesDescription",
                                            pokemon_species_form_description.id
                                        ),
                                        "text": pokemon_species_form_description.description
                                    }
                                ],
                                "formsSwitchable": pokemon_species.forms_switchable,
                                "genderRate": pokemon_species.gender_rate,
                                "genera": [
                                    {
                                        "id": get_id("PokemonSpeciesGenus", pokemon_species_name.id),
                                        "text": pokemon_species_name.genus
                                    }
                                ],
                                "generation": {
                                    "id": get_id(
                                        "Generation", pokemon_species.generation.id
                                    ),
                                    "name": pokemon_species.generation.name
                                },
                                "growthRate": {
                                    "id": get_id(
                                        "GrowthRate", pokemon_species.growth_rate.id
                                    ),
                                    "name": pokemon_species.growth_rate.name
                                },
                                "habitat": {
                                    "id": get_id(
                                        "PokemonHabitat", pokemon_species.pokemon_habitat.id
                                    ),
                                    "name": pokemon_species.pokemon_habitat.name
                                },
                                "hasGenderDifferences": pokemon_species.has_gender_differences,
                                "hatchCounter": pokemon_species.hatch_counter,
                                "isBaby": pokemon_species.is_baby,
                                "order": pokemon_species.order,
                                "pokedexNumbers": [
                                    {
                                        "id": get_id(
                                            "PokemonSpeciesPokedexEntry", dex_number.id
                                        ),
                                        "entryNumber": dex_number.pokedex_number,
                                        "node": {
                                            "id": get_id("Pokedex", pokedex.id),
                                            "name": pokedex.name,
                                        }
                                    }
                                ],
                                "shape": {
                                    "id": get_id("PokemonShape", shape.id),
                                    "name": shape.name,
                                },
                                "palParkEncounters": [
                                    {
                                        "id": get_id(
                                            "PokemonSpeciesPalParkEncounter",
                                            pal_park.id
                                        ),
                                        "baseScore": pal_park.base_score,
                                        "rate": pal_park.rate,
                                        "node": {
                                            "id": get_id(
                                                "PalParkArea", pal_park.pal_park_area.id
                                            ),
                                            "name": pal_park.pal_park_area.name,
                                        }
                                    }
                                ],
                                "varieties": [
                                    {
                                        "id": get_id("Pokemon", pokemon.id),
                                        "name": pokemon.name,
                                    }
                                ]
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
