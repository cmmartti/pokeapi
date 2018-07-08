# -*- coding: utf-8 -*-
import json
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseEffect, BaseFlavorText, BaseGenerationGameIndex
from ..loader_key import LoaderKey
from ..interfaces import RelayNode, SimpleEdge
from ..field import TranslationList


class ItemInterface(Interface):
    """
    ???
    """

    item_id = None
    name = String()
    names = TranslationList(
        lambda: ItemName,
        description="The name of this item listed in different languages."
    )
    attributes = List(
        lazy_import("pokemon_graphql.item_attribute.types.ItemAttribute"),
        description="A list of attributes this item has."
    )
    item_category_id = None
    category = Field(
        lazy_import("pokemon_graphql.item_category.types.ItemCategory"),
        description="The category of items this item falls into."
    )
    cost = Int(description="The price of this item in stores.")
    fling_power = Int(description="The power of the move Fling when used with this item.")
    item_fling_effect_id = None
    fling_effect = Field(
        lazy_import("pokemon_graphql.item_fling_effect.types.ItemFlingEffect"),
        description="The effect of the move Fling when used with this item."
    )
    effect_entries = TranslationList(
        lambda: ItemEffectText,
        description="The effect of this item listed in different languages."
    )
    flavor_text_entries = TranslationList(
        lambda: ItemFlavorText,
        description="The flavor text of this item listed in different languages."
    )
    game_indices = List(
        lambda: ItemGameIndex,
        description="A list of game indices relevent to this item by generation."
    )
    sprite = String(description="The default sprite used to depict this item in the game.")
    held_by_pokemon = relay.ConnectionField(
        lambda: ItemPokemonConnection,
        description="A list of Pokémon that might be found in the wild holding this item."
    )
    baby_trigger_for = Field(
        lazy_import("pokemon_graphql.evolution_chain.types.EvolutionChain"),
        description="An evolution chain this item requires to produce a baby during mating."
    )
    machines = List(
        lazy_import("pokemon_graphql.machine.types.Machine"),
        description="A list of the machines related to this item.",
        deprecation_reason="Do not use this field. It will be moved into a separate ItemInterface implementation for TH/HM machines at some point in the future. If you need it, create an issue on GitHub and it might get fast-tracked."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.item_id, **kwargs)
        return info.context.loaders.item_names.load(key)

    def resolve_attributes(self, info, **kwargs):
        key = LoaderKey(self.item_id, **kwargs)
        return info.context.loaders.item_attributes.load(key)

    def resolve_category(self, info):
        return info.context.loaders.itemcategory.load(self.item_category_id)

    def resolve_fling_effect(self, info):
        if not self.item_fling_effect_id:
            return None
        return info.context.loaders.itemflingeffect.load(self.item_fling_effect_id)

    def resolve_effect_entries(self, info, **kwargs):
        key = LoaderKey(self.item_id, **kwargs)
        return info.context.loaders.item_effectentries.load(key)

    def resolve_flavor_text_entries(self, info, **kwargs):
        key = LoaderKey(self.item_id, **kwargs)
        return info.context.loaders.item_flavortextentries.load(key)

    def resolve_game_indices(self, info, **kwargs):
        key = LoaderKey(self.item_id, **kwargs)
        return info.context.loaders.item_gameindices.load(key)

    def resolve_sprite(self, info):
        return info.context.loaders.item_sprites.load(self.item_id) \
            .then(ItemInterface.get_default_sprite)

    @staticmethod
    def get_default_sprite(sprites):
        sprites_data = json.loads(sprites.sprites)
        host = "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        if sprites_data["default"]:
            return host + sprites_data["default"].replace("/media/", "")
        return None

    def resolve_held_by_pokemon(self, info, **kwargs):
        q = models.Pokemon.objects.filter(pokemonitem__item_id=self.item_id).distinct()
        page = getPage(q, ItemPokemonConnection.__name__, **kwargs)

        edges = []
        for entry in page:
            edge = ItemPokemonConnection.Edge(
                node=entry,
                cursor=page.get_cursor(entry)
            )
            edge.item_id=self.item_id
            edge.pokemon_id=entry.id
            edges.append(edge)

        return ItemPokemonConnection(
            edges=edges,
            page_info=page.page_info,
            total_count=page.total_count,
        )

    def resolve_baby_trigger_for(self, info):
        return info.context.loaders.evolutionchain_by_item.load(self.item_id)

    def resolve_machines(self, info, **kwargs):
        key = LoaderKey(self.item_id, **kwargs)
        return info.context.loaders.item_machines.load(key)


class ItemName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemname.load(id)


class ItemEffectText(BaseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemeffect.load(id)


class ItemFlavorText(BaseFlavorText):
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group which uses this flavor text."
    )

    def resolve_version_group(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemflavortext.load(id)


class ItemGameIndex(BaseGenerationGameIndex):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemgameindex.load(id)


from ..pokemon.types import Pokemon
class ItemPokemonConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Pokemon

    class Edge:
        item_id = None
        pokemon_id = None
        versions = List(
            lambda: ItemPokemonVersion,
            description="The details for the version that this item is held in by the Pokémon."
        )

        def resolve_versions(self, info):
            key = LoaderKey(0, item_id=self.item_id, pokemon_id=self.pokemon_id)
            return info.context.loaders.pokemonitems_by_item_and_pokemon.load(key).then(
                ItemPokemonConnection.Edge.get_versions
            )

        @staticmethod
        def get_versions(pokemon_items):
            pkmn_item_versions = []
            for pi in pokemon_items:
                item_pokemon_version = ItemPokemonVersion()
                item_pokemon_version.rarity = pi.rarity
                item_pokemon_version.version_id = pi.version_id
                pkmn_item_versions.append(item_pokemon_version)
            return pkmn_item_versions


class ItemPokemonVersion(ObjectType):
    rarity = Int(description="How often this Pokémon holds this item in this version.")
    version_id = None
    node = Field(
        lazy_import("pokemon_graphql.version.types.Version"),
        description="The version that this item is held in by the Pokémon."
    )

    def resolve_node(self, info):
        return info.context.loaders.version.load(self.version_id)

    class Meta:
        interfaces = (SimpleEdge, )
