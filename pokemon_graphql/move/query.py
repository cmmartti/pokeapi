# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import MoveConnection, MoveOrdering
from ..where import Where


class Query(BaseQuery):
    moves = relay.ConnectionField(
        MoveConnection,
        description="A list of Pokémon moves that exist in the games.",
        where=Argument(Where),
        order_by=Argument(List(MoveOrdering))
    )

    def resolve_moves(self, info, **kwargs):
        q = models.Move.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, MoveConnection, **kwargs)
