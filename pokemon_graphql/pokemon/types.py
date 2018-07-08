# -*- coding: utf-8 -*-
import json
from graphene import Int, String, Boolean, Field, List, ObjectType, Enum, relay, Argument
from graphene import lazy_import

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseVersionGameIndex
from ..loader_key import LoaderKey
from ..interfaces import RelayNode, SimpleEdge
from ..field import TranslationList
from ..where import Where
from .id import PokemonHeldItemID
from .edges import *


class Pokemon(ObjectType):
    """
    Pokémon are the creatures that inhabit the world of the Pokémon games. They can be caught using Pokéballs and trained by battling with other Pokémon. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_%28species%29) for greater detail.
    """

    name = String(description="The name of this resource.")

    abilities = List(
        PokemonAbilityEdge,
        description="A list of abilities this Pokémon could potentially have."
    )
    def resolve_abilities(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_abilities.load(key)

    base_experience = Int(
        description="The base experience gained for defeating this Pokémon."
    )

    forms = List(
        lazy_import("pokemon_graphql.pokemon_form.types.PokemonForm"),
        description="A list of forms this Pokémon can take on."
    )
    def resolve_forms(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_forms.load(key)


    game_indices = List(
        lambda: PokemonGameIndex,
        description="A list of game indices relevent to Pokémon item by generation."
    )
    def resolve_game_indices(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_gameindices.load(key)

    height = Int(description="The height of this Pokémon.")

    held_items = List(
        PokemonHeldItem,
        description="A list of items this Pokémon may be holding when encountered."
    )
    def resolve_held_items(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_items.load(key).then(Pokemon.get_held_items)

    @staticmethod
    def get_held_items(data):
        held_items = set()
        for pokemon_item in data:
            id = PokemonHeldItemID(pokemon_item.item_id, pokemon_item.pokemon_id)
            held_item = PokemonHeldItem(id)
            held_item.item_id = pokemon_item.item_id
            held_item.pokemon_id = pokemon_item.pokemon_id
            held_items.add(held_item)

        return held_items

    is_default = Boolean(
        description="Set for exactly one Pokémon used as the default for each species."
    )

    location_area_encounters = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_encounter.types.PokemonEncounterConnection"),
        description="A list of location area encounters for this Pokémon."
    )
    def resolve_location_area_encounters(self, info, **kwargs):
        from ..pokemon_encounter.types import PokemonEncounterConnection

        q = models.LocationArea.objects.filter(encounter__pokemon_id=self.id).distinct()
        return getConnection(
            q, PokemonEncounterConnection,
            lambda data: Pokemon.get_pkmn_encounter(self, data),
            **kwargs
        )

    @staticmethod
    def get_pkmn_encounter(self, lctn_area):
        from ..pokemon_encounter.types import PokemonEncounter

        pkmn_encounter = PokemonEncounter()
        pkmn_encounter.location_area_id = lctn_area.id
        pkmn_encounter.pokemon_id = self.id
        return pkmn_encounter

    moves = relay.ConnectionField(
        PokemonMoveConnection,
        description="A list of moves along with learn methods and level details pertaining to specific version groups."
    )
    def resolve_moves(self, info, **kwargs):
        q = models.Move.objects.filter(pokemonmove__pokemon_id=self.id).distinct()
        page = getPage(q, PokemonMoveConnection.__name__, **kwargs)

        edges = []
        for entry in page:
            edge = PokemonMoveConnection.Edge(node=entry, cursor=page.get_cursor(entry))
            edge.pokemon_id = self.id
            edge.move_id = entry.id
            edges.append(edge)

        return PokemonMoveConnection(
            edges=edges,
            page_info=page.page_info,
            total_count=page.total_count,
        )

    order = Int(
        description="Order for sorting. Almost national order, except families are grouped together."
    )

    pokemon_species_id = None
    species = Field(
        lazy_import("pokemon_graphql.pokemon_species.types.PokemonSpecies"),
        description="The species this Pokémon belongs to."
    )
    def resolve_species(self, info, **kwargs):
        return info.context.loaders.pokemonspecies.load(self.pokemon_species_id)

    sprites = Field(
        lambda: PokemonSprites,
        description="A set of sprites used to depict this Pokémon in the game."
    )
    def resolve_sprites(self, info):
        return info.context.loaders.pokemon_sprites.load(self.id)

    stats = List(
        PokemonStat,
        description="A list of base stat values for this Pokémon."
    )
    def resolve_stats(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_stats.load(key)

    types = List(
        PokemonType,
        description="A list of details showing types this Pokémon has."
    )
    def resolve_types(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemon_types.load(key)

    weight = Int(description="The weight of this Pokémon.")

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemon.load(id)


class PokemonConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Pokemon


class PokemonOrderField(Enum):
    """Properties by which Pokemon connections can be ordered."""

    NAME = "name"

    @property
    def description(self):
        if self == PokemonOrderField.NAME:
            return "Order Pokémon by name."


class PokemonOrder(BaseOrder):
    """Ordering options for Pokemon connections."""
    field = PokemonOrderField(
        description="The field to order edges by.",
        required=True
    )


class PokemonGameIndex(BaseVersionGameIndex):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemongameindex.load(id)


class PokemonSprites(ObjectType):
    sprites = None
    front_default = String(
        description="The default depiction of this Pokémon from the front in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "front_default")
    )
    front_shiny = String(
        description="The shiny depiction of this Pokémon from the front in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "front_shiny")
    )
    front_female = String(
        description="The female depiction of this Pokémon from the front in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "front_female")
    )
    front_shiny_female = String(
        description="The shiny female depiction of this Pokémon from the front in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "front_shiny_female")
    )
    back_default = String(
        description="The default depiction of this Pokémon from the back in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "back_default")
    )
    back_shiny = String(
        description="The shiny depiction of this Pokémon from the back in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "back_shiny")
    )
    back_female = String(
        description="The female depiction of this Pokémon from the back in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "back_female")
    )
    back_shiny_female = String(
        description="The shiny female depiction of this Pokémon from the back in battle.",
        resolver=lambda root, i: PokemonSprites.get_sprite(root, "back_shiny_female")
    )

    @staticmethod
    def get_sprite(self, sprite_name):
        sprites_data = json.loads(self.sprites)
        host = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/'

        if sprites_data[sprite_name]:
            return host + sprites_data[sprite_name].replace('/media/', '')
        return None

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonsprites.load(id)
