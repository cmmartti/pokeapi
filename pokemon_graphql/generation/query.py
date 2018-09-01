# -*- coding: utf-8 -*-
from graphene import relay, Argument, List, Field, String
from django.core.exceptions import ObjectDoesNotExist

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import GenerationConnection, GenerationOrdering, Generation
from ..where import Where


class Query(BaseQuery):
    generations = relay.ConnectionField(
        GenerationConnection,
        description="A list of generations (groupings of games based on the Pokémon they include).",
        where=Argument(Where),
        order_by=Argument(List(GenerationOrdering))
    )

    def resolve_generations(self, info, **kwargs):
        q = models.Generation.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, GenerationConnection, **kwargs)

    generation = Field(Generation, name=String())

    def resolve_generation(self, info, **kwargs):
        if "name" in kwargs:
            try:
                return models.Generation.objects.get(name=kwargs["name"])
            except ObjectDoesNotExist:
                return None;
        else: return None;
