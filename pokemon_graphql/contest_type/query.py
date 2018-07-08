# -*- coding: utf-8 -*-
from graphene import List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import ContestType


class Query(BaseQuery):

    contest_types = List(
        ContestType,
        description="A list of contest types used to weigh a Pokémon's condition in Pokémon contests.",
        name=String()
    )

    def resolve_contest_types(self, info, **kwargs):
        q = models.ContestType.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs['name'])
        return q
