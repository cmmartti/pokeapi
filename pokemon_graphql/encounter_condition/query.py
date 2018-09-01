# -*- coding: utf-8 -*-
from graphene import List, String

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import EncounterCondition
from ..where import Where


class Query(BaseQuery):
    encounter_conditions = List(
        EncounterCondition,
        description="A list of conditions which affect what Pokémon might appear in the wild.",
        name=String()
    )

    def resolve_encounter_conditions(self, info, **kwargs):
        q = models.EncounterCondition.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs['name'])
        return q
