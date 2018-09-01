# -*- coding: utf-8 -*-
from graphene import Int, String, Boolean, Field, List, ObjectType, Enum, relay, Argument, InputObjectType, ID
from graphene import lazy_import

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class MoveDamageClass(ObjectType):
    """
    Damage classes moves can have, e.g. physical, special, or non-damaging.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: MoveDamageClassName,
        description="The name of this move damage class listed in different languages."
    )
    descriptions = TranslationList(
        lambda: MoveDamageClassDescription,
        description="The description of this move damage class listed in different languages."
    )
    moves = relay.ConnectionField(
        lazy_import("pokemon_graphql.move.types.MoveConnection"),
        description="A list of moves that fall into this damage class.",
        where=Argument(Where),
        order_by=Argument(List(lazy_import('pokemon_graphql.move.types.MoveOrdering')))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movedamageclass_names.load(key)

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movedamageclass_descriptions.load(key)

    def resolve_moves(self, info, **kwargs):
        from ..move.types import MoveConnection

        q = models.Move.objects.filter(move_damage_class_id=self.id)
        return getConnection(q, MoveConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movedamageclass.load(id)


class MoveDamageClassName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movedamageclassname.load(id)


class MoveDamageClassDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movedamageclassdescription.load(id)
