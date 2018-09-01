# -*- coding: utf-8 -*-
from graphene import List, String, Argument, Field
from django.core.exceptions import ObjectDoesNotExist

from pokemon_v2 import models
from ..base import BaseQuery
from ..pokemon_color.types import PokemonColor
from ..connections import getConnection
from ..where import Where


class Query(BaseQuery):

    pokemon_colors = List(
        PokemonColor,
        description="A list of colors used for sorting Pokémon in a Pokédex.",
        name=String()
    )

    def resolve_pokemon_colors(self, info, **kwargs):
        q = models.PokemonColor.objects.all()
        if "name" in kwargs:
            q = q.filter(name=kwargs["name"])
        return q

    pokemon_color = Field(PokemonColor, name=String())

    def resolve_pokemon_color(self, info, **kwargs):
        if "name" in kwargs:
            try:
                return models.PokemonColor.objects.get(name=kwargs["name"])
            except ObjectDoesNotExist:
                return None;
        else: return None;
