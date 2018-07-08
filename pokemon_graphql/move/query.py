# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import MoveConnection, MoveOrder
from ..where import Where


class Query(BaseQuery):
    moves = relay.ConnectionField(
        MoveConnection,
        description="A list of Pokémon moves that exist in the games.",
        order_by=Argument(MoveOrder),
        where=Argument(Where)
    )

    def resolve_moves(self, info, **kwargs):
        q = models.Move.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, MoveConnection, **kwargs)
