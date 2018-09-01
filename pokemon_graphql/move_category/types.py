# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class MoveCategory(ObjectType):
    """
    Very general categories that loosely group move effects.
    """

    name = String(description="The name of this resource.")
    descriptions = TranslationList(
        lambda: MoveCategoryDescription,
        description="The description of this move ailment listed in different languages1425."
    )
    moves = relay.ConnectionField(
        lazy_import("pokemon_graphql.move.types.MoveConnection"),
        description="A list of moves that fall into this category.",
        where=Argument(Where),
        order_by=Argument(List(lazy_import('pokemon_graphql.move.types.MoveOrdering')))
    )

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movemetacategory_descriptions.load(key)\

    def resolve_moves(self, info, **kwargs):
        from ..move.types import MoveConnection

        q = models.Move.objects.filter(movemeta__move_meta_category_id=self.id)
        return getConnection(q, MoveConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movemetacategory.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        return cls(id=data.id, name=data.name)


class MoveCategoryDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movemetacategorydescription.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        return cls(id=data.id, description=data.description)
