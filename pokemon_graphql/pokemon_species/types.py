# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseName, BaseDescription, BaseFlavorText, BaseTranslationObject
from ..loader_key import LoaderKey
from ..field import TranslationList
from ..interfaces import RelayNode, SimpleEdge


class PokemonSpecies(ObjectType):
    """
    A Pokémon Species forms the basis for at least one Pokémon. Attributes of a Pokémon species are shared across all varieties of Pokémon within the species. A good example is Wormadam; Wormadam is the species which can be found in three different varieties, Wormadam-Trash, Wormadam-Sandy and Wormadam-Plant.
    """

    name = String(description="The name of this resource.")

    names = TranslationList(
        lambda: PokemonSpeciesName,
        description="The name of this Pokémon species listed in different languages."
    )
    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonspecies_names.load(key)

    base_happiness = Int(
        description="The happiness when caught by a normal Pokéball; up to 255. The higher the number, the happier the Pokémon."
    )
    capture_rate = Int(
        description="The base capture rate; up to 255. The higher the number, the easier the catch."
    )

    pokemon_color_id = None
    color = Field(
        lazy_import("pokemon_graphql.pokemon_color.types.PokemonColor"),
        description="The color of this Pokémon for Pokédex search.",
        resolver=lambda rt, i: i.context.loaders.pokemoncolor.load(rt.pokemon_color_id)
    )

    egg_groups = List(
        lazy_import("pokemon_graphql.egg_group.types.EggGroup"),
        description="A list of egg groups this Pokémon species is a member of."
    )
    def resolve_egg_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.egggroups_by_pokemonspecies.load(key)

    evolution_chain_id = None
    evolution_chain = Field(
        lazy_import("pokemon_graphql.evolution_chain.types.EvolutionChain"),
        description="The evolution chain this Pokémon species is a member of."
    )
    def resolve_evolution_chain(self, info):
        return info.context.loaders.evolutionchain.load(self.evolution_chain_id)

    evolves_from_species_id = None
    evolves_from_species = Field(
        lambda: PokemonSpecies,
        description="The Pokémon species that evolves into this Pokemon_species."
    )
    def resolve_evolves_from_species(self, info):
        if not self.evolves_from_species_id:
            return None
        return info.context.loaders.pokemonspecies.load(self.evolves_from_species_id)

    flavor_text_entries = TranslationList(
        lambda: PokemonSpeciesFlavorText,
        description="A list of flavor text entries for this Pokémon species."
    )
    def resolve_flavor_text_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonspecies_flavortextentries.load(key)

    form_descriptions = TranslationList(
        lambda: PokemonSpeciesDescription,
        description="Descriptions of different forms Pokémon take on within the Pokémon species."
    )
    def resolve_form_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonspecies_descriptions.load(key)

    forms_switchable = Boolean(
        description="Whether or not this Pokémon has multiple forms and can switch between them."
    )
    gender_rate = Int(
        description="The chance of this Pokémon being female, in eighths; or -1 for genderless."
    )

    genera = TranslationList(
        lambda: PokemonSpeciesGenus,
        description="The genus of this Pokémon species listed in multiple languages."
    )
    def resolve_genera(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonspecies_names.load(key)

    generation_id = None
    generation = Field(
        lazy_import("pokemon_graphql.generation.types.Generation"),
        description="The generation this Pokémon species was introduced in.",
        resolver=lambda rt, i: i.context.loaders.generation.load(rt.generation_id)
    )
    growth_rate_id = None
    growth_rate = Field(
        lazy_import("pokemon_graphql.growth_rate.types.GrowthRate"),
        description="The rate at which this Pokémon species gains levels.",
        resolver=lambda rt, i: i.context.loaders.growthrate.load(rt.growth_rate_id)
    )
    pokemon_habitat_id = None
    habitat = Field(
        lazy_import("pokemon_graphql.pokemon_habitat.types.PokemonHabitat"),
        description="The habitat this Pokémon species can be encountered in.",
        resolver=lambda rt, i: i.context.loaders.pokemonhabitat.load(rt.pokemon_habitat_id)
    )
    has_gender_differences = Boolean(
        description="Whether or not this Pokémon has visual gender differences."
    )
    hatch_counter = Int(
        description="Initial hatch counter: one must walk 255 × (hatch_counter + 1) steps before this Pokémon's egg hatches, unless utilizing bonuses like Flame Body's."
    )
    is_baby = Boolean(
        description="Whether or not this is a baby Pokémon."
    )
    order = Int(
        description="The order in which species should be sorted. Based on National Dex order, except families are grouped together and sorted by stage."
    )
    pokedex_numbers = List(
        lambda: PokemonSpeciesPokedexEntry,
        description="A list of Pokedexes and the indexes reserved within them for this Pokémon species."
    )
    def resolve_pokedex_numbers(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonspecies_dexnumbers.load(key)

    pokemon_shape_id = None
    shape = Field(
        lazy_import("pokemon_graphql.pokemon_shape.types.PokemonShape"),
        description="The shape of this Pokémon for Pokédex search.",
        resolver=lambda rt, i: i.context.loaders.pokemonshape.load(rt.pokemon_shape_id)
    )
    pal_park_encounters = List(
        lambda: PokemonSpeciesPalParkEncounter,
        description="A list of encounters that can be had with this Pokémon species in pal park."
    )
    def resolve_pal_park_encounters(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.palparks_by_pokemonspecies.load(key)

    varieties = List(
        lazy_import("pokemon_graphql.pokemon.types.Pokemon"),
        description="A list of the Pokémon that exist within this Pokémon species."
    )
    def resolve_varieties(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_by_pokemonspecies.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonspecies.load(id)


class PokemonSpeciesName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonspeciesname.load(id)


class PokemonSpeciesFlavorText(BaseFlavorText):
    version_id = None
    version = Field(
        lazy_import("pokemon_graphql.version.types.Version"),
        description="The version relevent to this flavor text.",
        resolver=lambda root, info: info.context.loaders.version.load(root.version_id)
    )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonspeciesflavortext.load(id)


class PokemonSpeciesDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonspeciesdescription.load(id)


class PokemonSpeciesGenus(BaseTranslationObject):
    genus = String(
        name="text",
        description="The localized genus for the referenced Pokémon species."
    )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonspeciesname.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, genus=data.genus)
        obj.language_id = data.language_id
        return obj


class PokemonSpeciesPokedexEntry(ObjectType):
    pokedex_number = Int(
        name="entryNumber",
        description="The index number within the Pokédex."
    )
    pokedex_id = None
    node = Field(
        lazy_import("pokemon_graphql.pokedex.types.Pokedex"),
        description="The Pokédex the referenced Pokémon species can be found in."
    )

    def resolve_node(self, info):
        return info.context.loaders.pokedex.load(self.pokedex_id)

    class Meta:
        interfaces = (RelayNode, SimpleEdge)

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemondexnumber.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, pokedex_number=data.pokedex_number)
        obj.pokedex_id = data.pokedex_id
        return obj


class PokemonSpeciesPalParkEncounter(ObjectType):
    base_score = Int(
        description="The base score given to the player when the referenced Pokémon is caught during a pal park run."
    )
    rate = Int(
        description="The base rate for encountering the referenced Pokémon in this pal park area."
    )
    pal_park_area_id = None
    node = Field(
        lazy_import("pokemon_graphql.pal_park_area.types.PalParkArea"),
        description="The pal park area where this encounter happens."
    )

    def resolve_node(self, info):
        return info.context.loaders.palparkarea.load(self.pal_park_area_id)

    class Meta:
        interfaces = (RelayNode, SimpleEdge)

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.palpark.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, base_score=data.base_score, rate=data.rate)
        obj.pal_park_area_id = data.pal_park_area_id
        return obj
