# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..pokemon_form.types import PokemonFormConnection, PokemonFormOrdering
from ..connections import getConnection
from ..where import Where


class Query(BaseQuery):

    pokemon_forms = relay.ConnectionField(
        PokemonFormConnection,
        description="A list of different forms some Pokémon can take on.",
        where=Argument(Where),
        order_by=Argument(List(PokemonFormOrdering))
    )

    def resolve_pokemon_forms(self, info, **kwargs):
        q = models.PokemonForm.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, PokemonFormConnection, **kwargs)
