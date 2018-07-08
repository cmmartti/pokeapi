# -*- coding: utf-8 -*-
import json
from graphene import *

from ..loader_key import LoaderKey
from ..interfaces import RelayNode, SimpleEdge
from ..item.types import ItemInterface


class Berry(ObjectType):
    """
    Berries are small fruits that can provide HP and status condition restoration, stat enhancement, and even damage negation when eaten by Pokémon. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Berry) for greater detail.
    """

    class Meta:
        interfaces = (RelayNode, ItemInterface)

    berry_id = None
    growth_time = Int(
        description="Time it takes the tree to grow one stage, in hours. Berry trees go through four of these growth stages before they can be picked."
    )
    max_harvest = Int(
        description="The maximum number of these berries that can grow on one tree in Generation IV."
    )
    natural_gift_power = Int(
        description="The power of the move \"Natural Gift\" when used with this Berry."
    )
    size = Int(description="The size of this Berry, in millimetres.")
    smoothness = Int(
        description="The smoothness of this Berry, used in making Pokéblocks or Poffins."
    )
    soil_dryness = Int(
        description="The speed at which this Berry dries out the soil as it grows. A higher rate means the soil dries more quickly."
    )
    berry_firmness_id = None
    firmness = Field(
        lazy_import("pokemon_graphql.berry_firmness.types.BerryFirmness"),
        description="The firmness of this berry, used in making Pokéblocks or Poffins."
    )
    flavors = List(
        lambda: BerryFlavorMap,
        description="A list of references to each flavor a berry can have and the potency of each of those flavors in regard to this berry."
    )
    natural_gift_type_id = None
    natural_gift_type = Field(
        lazy_import("pokemon_graphql.type.types.Type"),
        description="The type inherited by \"Natural Gift\" when used with this Berry."
    )

    def resolve_firmness(self, info):
        return info.context.loaders.berryfirmness.load(self.berry_firmness_id)

    def resolve_flavors(self, info, **kwargs):
        key = LoaderKey(self.berry_id, **kwargs)
        return info.context.loaders.berry_flavormaps.load(key)

    def resolve_natural_gift_type(self, info):
        return info.context.loaders.type.load(self.natural_gift_type_id)

    @classmethod
    def get_node(cls, info, item_id):
        from ..item_interface.connection import get_item_node

        return info.context.loaders.item.load(item_id).then(get_item_node)


class BerryFlavorMap(ObjectType):
    berry_flavor_id = None
    node = Field(
        lazy_import("pokemon_graphql.berry_flavor.types.BerryFlavor"),
        description="The referenced berry flavor."
    )
    potency = Int(description="How powerful the referenced flavor is for this berry.")

    def resolve_node(self, info):
        return info.context.loaders.berryflavor.load(self.berry_flavor_id)

    class Meta:
        interfaces = (SimpleEdge, )
