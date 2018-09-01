# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .connection import (
    PokemonSpeciesConnection as Connection,
    PokemonSpeciesOrdering as Ordering,
    PokemonSpeciesWhere as Where
)


class Query(BaseQuery):
    pokemon_species = relay.ConnectionField(
        Connection,
        description="A list of Pokémon species.",
        where=Argument(Where),
        order_by=List(Ordering)
    )

    def resolve_pokemon_species(self, info, **kwargs):
        q = models.PokemonSpecies.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        q = Ordering.apply(q, kwargs.get("order_by", []))
        return getConnection(q, Connection, **kwargs)
