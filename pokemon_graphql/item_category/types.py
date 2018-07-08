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


class ItemCategory(ObjectType):
    """
    Item categories determine where items will be placed in the players bag.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: ItemCategoryName,
        description="The name of this item category listed in different languages."
    )
    items = relay.ConnectionField(
        lazy_import("pokemon_graphql.item_interface.connection.ItemInterfaceConnection"),
        description="A list of items that are a part of this category."
    )
    item_pocket_id = None
    pocket = Field(
        lazy_import("pokemon_graphql.item_pocket.types.ItemPocket"),
        description="The pocket items in this category would be put in."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itemcategory_names.load(key)

    def resolve_pocket(self, info, **kwargs):
        return info.context.loaders.itempocket.load(self.item_pocket_id)

    def resolve_items(self, info, **kwargs):
        from ..item_interface.connection import getItemConnection

        q = models.Item.objects.filter(item_category_id=self.id)
        return getItemConnection(q, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemcategory.load(id)


class ItemCategoryName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemcategoryname.load(id)
