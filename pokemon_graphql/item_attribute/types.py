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


class ItemAttribute(ObjectType):
    """
    Item attributes define particular aspects of items, e.g. "usable in battle" or "consumable".
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: ItemAttributeName,
        description="The name of this item attribute listed in different languages."
    )
    descriptions = TranslationList(
        lambda: ItemAttributeDescription,
        description="The description of this item attribute listed in different languages."
    )
    items = relay.ConnectionField(
        lazy_import("pokemon_graphql.item_interface.connection.ItemInterfaceConnection"),
        description="A list of items that have this attribute."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itemattribute_names.load(key)

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.itemattribute_descriptions.load(key)

    def resolve_items(self, info, **kwargs):
        from ..item_interface.connection import getItemConnection

        q = models.Item.objects.filter(itemattributemap__item_attribute_id=self.id)
        return getItemConnection(q, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemattribute.load(id)


class ItemAttributeName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemattributename.load(id)


class ItemAttributeDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.itemattributedescription.load(id)
