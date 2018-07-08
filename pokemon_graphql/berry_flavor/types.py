# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..base import BaseName
from ..interfaces import SimpleEdge
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..item_interface.connection import get_item_node


class BerryFlavor(ObjectType):
    """
    Flavors determine whether a Pokémon will benefit or suffer from eating a berry based on their nature. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Flavor) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: BerryFlavorName,
        description="The flavor text of this berry flavor listed in different languages."
    )
    contest_type_id = None
    contest_type = Field(
        lazy_import("pokemon_graphql.contest_type.types.ContestType"),
        description="The contest type that correlates with this berry flavor."
    )
    berries = List(
        lambda: BerryFlavorBerryEdge,
        description="A list of the berry items with this flavor."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.berryflavor_names.load(key)

    def resolve_contest_type(self, info):
        return info.context.loaders.contesttype.load(self.contest_type_id)

    def resolve_berries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.berryflavor_maps.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.berryflavor.load(id)


class BerryFlavorName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.berryflavorname.load(id)


class BerryFlavorBerryEdge(ObjectType):
    potency = Int(description="How powerful the referenced flavor is for this berry.")
    berry_id = Int()
    node = Field(
        lazy_import("pokemon_graphql.berry.types.Berry"),
        description="The berry item with the referenced flavor."
    )

    def resolve_node(self, info):
        return info.context.loaders.item_by_berry.load(self.berry_id).then(
            lambda item: get_item_node(item)
        )

    class Meta:
        interfaces = (SimpleEdge, )
