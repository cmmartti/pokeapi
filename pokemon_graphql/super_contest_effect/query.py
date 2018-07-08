# -*- coding: utf-8 -*-
from graphene import List, Int

from pokemon_v2 import models
from ..base import BaseQuery
from .types import SuperContestEffect


class Query(BaseQuery):

    super_contest_effects = List(
        SuperContestEffect,
        description="A list of move effects when used in super contests.",
        id=Int()
    )

    def resolve_super_contest_effects(self, info, **kwargs):
        q = models.SuperContestEffect.objects.all()
        if "id" in kwargs: q = q.filter(id=kwargs['id'])
        return q
