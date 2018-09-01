# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import PokedexConnection, PokedexOrdering
from ..where import Where


class Query(BaseQuery):
    pokedexes = relay.ConnectionField(
        PokedexConnection,
        description="A list of machines that teach moves to Pokémon.",
        where=Argument(Where),
        order_by=Argument(List(PokedexOrdering))
    )

    def resolve_pokedexes(self, info, **kwargs):
        q = models.Pokedex.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, PokedexConnection, **kwargs)
