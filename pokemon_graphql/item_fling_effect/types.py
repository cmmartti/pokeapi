# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseEffect
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class ItemFlingEffect(ObjectType):
    """
    The various effects of the move "Fling" when used with different items.
    """

    name = String(description="The name of this resource.")
    effect_entries = TranslationList(
        lambda: ItemFlingEffectEffectText,
        description="The result of this fling effect listed in different languages."
    )
    items = List(
        lazy_import("pokemon_graphql.item_interface.types.ItemInterface"),
        description="A list of items that have this fling effect."
    )

    def resolve_effect_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itemflingeffect_effectentries.load(key)

    def resolve_items(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itemflingeffect_items.load(key).then(
            ItemFlingEffect.get_items
        )

    @staticmethod
    def get_items(items):
        from ..item_interface.connection import get_item_node
        return [get_item_node(item) for item in items]

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemflingeffect.load(id)


class ItemFlingEffectEffectText(BaseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemflingeffecteffecttext.load(id)
