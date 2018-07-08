# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class ItemPocket(ObjectType):
    """
    Pockets within the players bag used for storing items by category.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: ItemPocketName,
        description="The name of this item category listed in different languages."
    )
    categories = List(
        lazy_import("pokemon_graphql.item_category.types.ItemCategory"),
        description="A list of item categories that are relevant to this item pocket."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itempocket_names.load(key)

    def resolve_categories(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itempocket_categories.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itempocket.load(id)


class ItemPocketName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itempocketname.load(id)
