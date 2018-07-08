# -*- coding: utf-8 -*-
from graphene import List, Int

from pokemon_v2 import models
from ..base import BaseQuery
from .types import ContestEffect


class Query(BaseQuery):

    contest_effects = List(
        ContestEffect,
        description="A list of move effects when used in contests.",
        id=Int()
    )

    def resolve_contest_effects(self, info, **kwargs):
        q = models.ContestEffect.objects.all()
        if "id" in kwargs: q = q.filter(id=kwargs['id'])
        return q
