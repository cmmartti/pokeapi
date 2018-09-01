# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import NatureConnection, NatureOrdering
from ..where import Where


class Query(BaseQuery):
    natures = relay.ConnectionField(
        NatureConnection,
        description="A list of natures that influence how a Pokémon's stats grow.",
        where=Argument(Where),
        order_by=Argument(List(NatureOrdering))
    )

    def resolve_natures(self, info, **kwargs):
        q = models.Nature.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, NatureConnection, **kwargs)
