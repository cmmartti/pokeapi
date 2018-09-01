# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class Nature(ObjectType):
    """
    Natures influence how a Pokémon's stats grow. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Nature) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: NatureName,
        description="The name of this nature listed in different languages."
    )
    decreased_stat_id = None
    decreased_stat = Field(
        lazy_import("pokemon_graphql.stat.types.Stat"),
        description="The stat decreased by 10% in Pokémon with this nature."
    )
    increased_stat_id = None
    increased_stat = Field(
        lazy_import("pokemon_graphql.stat.types.Stat"),
        description="The stat increased by 10% in Pokémon with this nature."
    )
    hates_flavor_id = None
    hates_flavor = Field(
        lazy_import("pokemon_graphql.berry_flavor.types.BerryFlavor"),
        description="The berry flavour hated by Pokémon with this nature."
    )
    likes_flavor_id = None
    likes_flavor = Field(
        lazy_import("pokemon_graphql.berry_flavor.types.BerryFlavor"),
        description="The berry flavour liked by Pokémon with this nature."
    )
    pokeathlon_stat_changes = List(
        lambda: NatureStatChange,
        description="A list of Pokéathlon stats this nature effects and how much it effects them."
    )
    move_battle_style_preferences = List(
        lambda: MoveBattleStylePreference,
        description="A list of battle styles and how likely a Pokémon with this nature is to use them in the Battle Palace or Battle Tent."
    )


    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.nature_names.load(key)

    def resolve_decreased_stat(self, info):
        if not self.decreased_stat_id:
            return None
        return info.context.loaders.stat.load(self.decreased_stat_id)

    def resolve_increased_stat(self, info):
        if not self.increased_stat_id:
            return None
        return info.context.loaders.stat.load(self.increased_stat_id)

    def resolve_hates_flavor(self, info):
        return info.context.loaders.berryflavor.load(self.hates_flavor_id)

    def resolve_likes_flavor(self, info):
        return info.context.loaders.berryflavor.load(self.likes_flavor_id)

    def resolve_pokeathlon_stat_changes(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.nature_statchanges.load(key)

    def resolve_move_battle_style_preferences(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.nature_battlestylepreferences.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.nature.load(id)


class NatureConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Nature


class NatureOrdering(BaseOrder):
    sort = InputField(
        Enum('NatureSort', [("NAME", "name")]),
        description="The field to sort by."
    )


class NatureName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.naturename.load(id)


class NatureStatChange(ObjectType):
    max_change = Int(description="The amount of change.")
    pokeathlon_stat_id = None
    node = Field(
        lazy_import("pokemon_graphql.pokeathlon_stat.types.PokeathlonStat"),
        description="The stat being affected."
    )

    def resolve_node(self, info):
        return info.context.loaders.pokeathlonstat.load(self.pokeathlon_stat_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.naturepokeathlonstat.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, max_change=data.max_change)
        obj.pokeathlon_stat_id = data.pokeathlon_stat_id
        return obj


class MoveBattleStylePreference(ObjectType):
    low_hp_preference = Int(
        name="lowHPPreference",
        description="Chance of using the move, in percent, if HP is under one half."
    )
    high_hp_preference = Int(
        name="highHPPreference",
        description="Chance of using the move, in percent, if HP is over one half."
    )
    move_battle_style_id = None
    node = Field(
        lazy_import("pokemon_graphql.move_battle_style.types.MoveBattleStyle"),
        description="The move battle style."
    )

    def resolve_node(self, info):
        return info.context.loaders.movebattlestyle.load(self.move_battle_style_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.naturebattlestylepreference.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(
            id=data.id,
            low_hp_preference=data.low_hp_preference,
            high_hp_preference=data.high_hp_preference
        )
        obj.move_battle_style_id = data.move_battle_style_id
        return obj
