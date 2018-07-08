# -*- coding: utf-8 -*-
from graphene import List, Argument, String

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from ..pokeathlon_stat.types import PokeathlonStat
from ..where import Where


class Query(BaseQuery):
    pokeathlon_stats = List(
        PokeathlonStat,
        description="A list of Pokéathlon stats, attributes of a Pokémon's performance in Pokéathlons.",
        name=String()
    )

    def resolve_pokeathlon_stats(self, info, **kwargs):
        q = models.PokeathlonStat.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
