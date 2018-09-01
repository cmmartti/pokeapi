# -*- coding: utf-8 -*-
from graphene import *

from ..base import BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..item_interface.connection import get_item_node


class BerryFirmness(ObjectType):
    """
    Berry firmness determines the smoothness of the Pokéblock produced from a berry ([Pokéblocks](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9block) are colorful candy blocks made for Pokémon, primarily used to increase a Pokémon's condition for Pokémon Contests; also known as [Poffins]).(https://bulbapedia.bulbagarden.net/wiki/Poffin)
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: BerryFirmnessName,
        description="The flavor text of this berry firmness listed in different languages."
    )
    berries = List(
        lazy_import("pokemon_graphql.berry.types.Berry"),
        description="A list of the berry items with this firmness."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.berryfirmness_names.load(key)

    def resolve_berries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.berryfirmness_items.load(key).then(
            lambda items: [get_item_node(item) for item in items]
        )


    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.berryfirmness.load(id)


class BerryFirmnessName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.berryfirmnessname.load(id)
