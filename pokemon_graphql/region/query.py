# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import RegionConnection, RegionOrder
from ..where import Where


class Query(BaseQuery):
    regions = relay.ConnectionField(
        RegionConnection,
        description="A list of regions (organized areas) of the Pokémon world.",
        where=Argument(Where), order_by=Argument(RegionOrder)
    )

    def resolve_regions(self, info, **kwargs):
        q = models.Region.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, RegionConnection, **kwargs)
