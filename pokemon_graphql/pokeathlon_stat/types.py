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


class PokeathlonStat(ObjectType):
    """
    Pokeathlon Stats are different attributes of a Pokémon's performance in Pokéathlons. In Pokéathlons, competitions happen on different courses; one for each of the different Pokéathlon stats. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9athlon) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: PokeathlonStatName,
        description="The name of this Pokéathlon stat listed in different languages."
    )
    affecting_natures = relay.ConnectionField(
        lambda: PokeathlonStatAffectNatureConnection,
        description="A list of natures which affect this Pokéathlon stat.",
        where=Argument(lambda: PokeathlonStatAffectNatureWhere),
        order_by=Argument(lambda: PokeathlonStatAffectNatureOrder)
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokeathlonstat_names.load(key)

    def resolve_affecting_natures(self, info, **kwargs):
        q = models.NaturePokeathlonStat.objects.filter(pokeathlon_stat_id=self.id)
        q = q.select_related("nature")
        q = PokeathlonStatAffectNatureWhere.apply(q, **kwargs.get("where", {}))

        page = getPage(q, PokeathlonStatAffectNatureConnection.__name__, **kwargs)

        return PokeathlonStatAffectNatureConnection(
            edges=[
                PokeathlonStatAffectNatureConnection.Edge(
                    node=entry.nature,
                    max_change=entry.max_change,
                    cursor=page.get_cursor(entry),
                ) for entry in page
            ],
            page_info=page.page_info,
            total_count=page.total_count,
        )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokeathlonstat.load(id)


class PokeathlonStatName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokeathlonstatname.load(id)


from ..nature.types import Nature
class PokeathlonStatAffectNatureConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Nature

    class Edge:
        max_change = Int(
            description="The maximum amount of change to the referenced Pokéathlon stat."
        )


class PokeathlonStatAffectNatureOrderField(Enum):
    """Properties by which Pokéathlon stat affect nature connections can be ordered."""
    NAME = "name"
    MAX_CHANGE = "max_change"

    @property
    def description(self):
        if self == PokeathlonStatAffectNatureOrderField.NAME:
            return "Order by the name of the move."
        if self == PokeathlonStatAffectNatureOrderField.MAX_CHANGE:
            return "Order by the amount of maxChange each nature causes in the Pokéathlon stat."


class PokeathlonStatAffectNatureOrder(BaseOrder):
    """Ordering options for Pokéathlon stat affect nature connections."""

    field = PokeathlonStatAffectNatureOrderField(
        description="The field to order edges by.",
        required=True
    )


class PokeathlonStatAffectNatureWhere(BaseWhere):
    """Filtering options for Pokéathlon stat affect nature connections. To include only natures with a positive stat change, set `maxChange_gt` to `0`. You can create separate queries for positive and negative changes using [aliases](https://graphql.org/learn/queries/#aliases)."""

    max_change__gt = Int(
        name="maxChange_gt",
        description="Only include natures that have a Pokéathlon stat change greater than _x_."
    )
    max_change__lt = Int(
        name="maxChange_lt",
        description="Only include natures that have a Pokéathlon stat change less than _x_."
    )
