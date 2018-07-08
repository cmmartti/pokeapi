# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import PokedexConnection, PokedexOrder
from ..where import Where


class Query(BaseQuery):
    pokedexes = relay.ConnectionField(
        PokedexConnection,
        description="A list of machines that teach moves to Pokémon.",
        order_by=Argument(PokedexOrder),
        where=Argument(Where)
    )

    def resolve_pokedexes(self, info, **kwargs):
        q = models.Pokedex.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, PokedexConnection, **kwargs)
