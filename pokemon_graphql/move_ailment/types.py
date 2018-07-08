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


class MoveAilment(ObjectType):
    """
    Move Ailments are status conditions caused by moves used during battle. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/http://bulbapedia.bulbagarden.net/wiki/Status_condition) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: MoveAilmentName,
        description="The name of this move ailment listed in different languages."
    )
    moves = relay.ConnectionField(
        lazy_import("pokemon_graphql.move.types.MoveConnection"),
        description="A list of moves that cause this ailment.",
        where=Argument(Where),
        order_by=Argument(lazy_import("pokemon_graphql.move.types.MoveOrder"))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movemetaailment_names.load(key)

    def resolve_moves(self, info, **kwargs):
        from ..move.types import MoveConnection
        q = models.Move.objects.filter(movemeta__move_meta_ailment_id=self.id)
        return getConnection(q, MoveConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movemetaailment.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        return cls(id=data.id, name=data.name)


class MoveAilmentName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movemetaailmentname.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, name=data.name)
        obj.language_id = data.language_id
        return obj
