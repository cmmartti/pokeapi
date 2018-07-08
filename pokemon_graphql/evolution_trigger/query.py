# -*- coding: utf-8 -*-
from graphene import List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import EvolutionTrigger


class Query(BaseQuery):

    evolution_triggers = List(
        EvolutionTrigger,
        description="A list of evolution triggers.",
        name=String()
    )

    def resolve_evolution_triggers(self, info, **kwargs):
        q = models.EvolutionTrigger.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs['name'])
        return q
