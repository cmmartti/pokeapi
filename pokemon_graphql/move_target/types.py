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


class MoveTarget(ObjectType):
    """
    Targets that moves can be directed at during battle. Targets can be Pokémon, environments or even other moves.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: MoveTargetName,
        description="The name of this move target listed in different languages."
    )
    descriptions = TranslationList(
        lambda: MoveTargetDescription,
        description="The description of this move target listed in different languages."
    )
    moves = relay.ConnectionField(
        lazy_import("pokemon_graphql.move.types.MoveConnection"),
        description="A list of moves that that are directed at this target.",
        where=Argument(Where),
        order_by=Argument(lazy_import("pokemon_graphql.move.types.MoveOrder"))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movetarget_names.load(key)

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movetarget_descriptions.load(key)\

    def resolve_moves(self, info, **kwargs):
        from ..move.types import MoveConnection

        q = models.Move.objects.filter(move_target_id=self.id)
        return getConnection(q, MoveConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movetarget.load(id)


class MoveTargetName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movetargetname.load(id)


class MoveTargetDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movetargetdescription.load(id)
