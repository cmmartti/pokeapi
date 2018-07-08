# -*- coding: utf-8 -*-
from graphene import List, String, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..pokemon_habitat.types import PokemonHabitat
from ..connections import getConnection
from ..where import Where


class Query(BaseQuery):

    pokemon_habitats = List(
        PokemonHabitat,
        description="A list of habitats that Pokémon can be found in (e.g. cave).",
        name=String()
    )

    def resolve_pokemon_habitats(self, info, **kwargs):
        q = models.PokemonHabitat.objects.all()
        if "name" in kwargs:
            q = q.filter(name=kwargs["name"])
        return q
