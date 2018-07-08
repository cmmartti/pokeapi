# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import BaseWhere


class Stat(ObjectType):
    """
    Stats determine certain aspects of battles. Each Pokémon has a value for each stat which grows as they gain levels and can be altered momentarily by effects in battles.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: StatName,
        description="The name of this stat listed in different languages."
    )
    game_index = Int(description="ID the games use for this stat.")
    is_battle_only = Boolean(
        description="Whether this stat only exists within a battle."
    )
    affecting_moves = relay.ConnectionField(
        lambda: StatAffectMoveConnection,
        description="A list of moves which affect this stat.",
        where=Argument(lambda: StatAffectMoveWhere),
        order_by=Argument(lambda: StatAffectMoveOrder)
    )
    characteristics = List(
        lazy_import("pokemon_graphql.characteristic.types.Characteristic"),
        description="A list of characteristics that are set on a Pokémon when its highest base stat is this stat."
    )
    move_damage_class_id = None
    move_damage_class = Field(
        lazy_import("pokemon_graphql.move_damage_class.types.MoveDamageClass"),
        description="The class of damage this stat is directly related to."
    )
    positive_affecting_natures = List(
        lazy_import("pokemon_graphql.nature.types.Nature"),
        description="A list of natures which affect this stat positively."
    )
    negative_affecting_natures = List(
        lazy_import("pokemon_graphql.nature.types.Nature"),
        description="A list of natures which affect this stat negatively."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.stat_names.load(key)

    def resolve_affecting_moves(self, info, **kwargs):
        q = models.MoveMetaStatChange.objects.filter(stat_id=self.id)
        q = q.select_related("move")
        q = StatAffectMoveWhere.apply(q, **kwargs.get("where", {}))

        page = getPage(q, StatAffectMoveConnection.__name__, **kwargs)
        return StatAffectMoveConnection(
            edges=[
                StatAffectMoveConnection.Edge(
                    node=entry.move,
                    change=entry.change,
                    cursor=page.get_cursor(entry),
                ) for entry in page
            ],
            page_info=page.page_info,
            total_count=page.total_count,
        )

    def resolve_characteristics(self, info):
        key = LoaderKey(self.id)
        return info.context.loaders.characteristics_by_stat.load(key)

    def resolve_move_damage_class(self, info):
        if not self.move_damage_class_id:
            return None
        return info.context.loaders.movedamageclass.load(self.move_damage_class_id)

    def resolve_positive_affecting_natures(self, info):
        key = LoaderKey(self.id)
        return info.context.loaders.natures_by_increasedstat.load(key)

    def resolve_negative_affecting_natures(self, info):
        key = LoaderKey(self.id)
        return info.context.loaders.natures_by_decreasedstat.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.stat.load(id)


class StatName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.statname.load(id)


from ..move.types import Move
class StatAffectMoveConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Move

    class Edge:
        change = Int(
            description="The maximum amount of change to the referenced stat."
        )


class StatAffectMoveOrderField(Enum):
    """Properties by which stat affect move connections can be ordered."""
    NAME = "name"
    CHANGE = "change"

    @property
    def description(self):
        if self == StatAffectMoveOrderField.NAME:
            return "Order by the name of the move."
        if self == StatAffectMoveOrderField.CHANGE:
            return "Order by the amount of change each move causes in the stat."


class StatAffectMoveOrder(BaseOrder):
    """Ordering options for stat affect move connections."""

    field = StatAffectMoveOrderField(
        description="The field to order edges by.",
        required=True
    )


class StatAffectMoveWhere(BaseWhere):
    """Filtering options for stat affect move connections. To include only moves with a positive stat change, set `change_gt` to `0`. You can create separate queries for positive and negative stat changes using [aliases](https://graphql.org/learn/queries/#aliases)."""

    change__gt = Int(
        name="change_gt",
        description="Only include moves that have a stat change greater than _x_."
    )
    change__lt = Int(
        name="change_lt",
        description="Only include moves that have a stat change less than _x_."
    )
