# -*- coding: utf-8 -*-
from graphene import Argument, relay

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import PokemonConnection, PokemonOrder
from ..where import Where


class Query(BaseQuery):
    pokemons = relay.ConnectionField(
        PokemonConnection,
        description="A list of Pokémon.",
        order_by=Argument(PokemonOrder),
        where=Argument(Where)
    )

    def resolve_pokemons(self, info, **kwargs):
        q = models.Pokemon.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, PokemonConnection, **kwargs)
