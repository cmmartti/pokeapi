# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import TypeConnection, TypeOrder
from ..where import Where


class Query(BaseQuery):
    types = relay.ConnectionField(
        TypeConnection,
        description="A list of types Pokémon and moves can have.",
        where=Argument(Where),
        order_by=Argument(TypeOrder)
    )

    def resolve_types(self, info, **kwargs):
        q = models.Type.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, TypeConnection, **kwargs)
