# -*- coding: utf-8 -*-
from graphene import List, String, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..pokemon_shape.types import PokemonShape
from ..connections import getConnection
from ..where import Where


class Query(BaseQuery):

    pokemon_shapes = List(
        PokemonShape,
        description="A list of shapes used for sorting Pokémon in a Pokédex.",
        name=String()
    )

    def resolve_pokemon_shapes(self, info, **kwargs):
        q = models.PokemonShape.objects.all()
        if "name" in kwargs:
            q = q.filter(name=kwargs["name"])
        return q
