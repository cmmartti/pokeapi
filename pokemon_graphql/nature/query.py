# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import NatureConnection, NatureOrder
from ..where import Where


class Query(BaseQuery):
    natures = relay.ConnectionField(
        NatureConnection,
        description="A list of natures that influence how a Pokémon's stats grow.",
        order_by=Argument(NatureOrder),
        where=Argument(Where)
    )

    def resolve_natures(self, info, **kwargs):
        q = models.Nature.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, NatureConnection, **kwargs)
