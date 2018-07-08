# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import PokemonSpeciesConnection, PokemonSpeciesOrder
from ..where import Where


class Query(BaseQuery):
    pokemon_species = relay.ConnectionField(
        PokemonSpeciesConnection,
        description="A list of Pokémon species.",
        order_by=Argument(PokemonSpeciesOrder),
        where=Argument(Where)
    )

    def resolve_pokemon_species(self, info, **kwargs):
        q = models.PokemonSpecies.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, PokemonSpeciesConnection, **kwargs)
