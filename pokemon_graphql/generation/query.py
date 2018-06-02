# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import GenerationConnection, GenerationOrder
from ..where import Where


class Query(BaseQuery):
    generations = relay.ConnectionField(
        GenerationConnection,
        description="A list of generations (groupings of games based on the Pokémon they include).",
        where=Argument(Where), order_by=Argument(GenerationOrder)
    )

    def resolve_generations(self, info, **kwargs):
        q = models.Generation.objects.all()
        return getConnection(q, GenerationConnection, **kwargs)
