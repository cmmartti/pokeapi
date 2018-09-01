# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .connection import (
    PokemonConnection as Connection,
    PokemonOrdering as Ordering,
    PokemonWhere as Where
)


class Query(BaseQuery):
    pokemons = relay.ConnectionField(
        Connection,
        description="A list of Pokémon varieties.",
        where=Argument(Where),
        order_by=List(Ordering)
    )

    def resolve_pokemons(self, info, **kwargs):
        q = models.Pokemon.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, Connection, **kwargs)
