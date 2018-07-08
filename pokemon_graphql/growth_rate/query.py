# -*- coding: utf-8 -*-
from graphene import List, Argument, String

from pokemon_v2 import models
from ..base import BaseQuery
from ..growth_rate.types import GrowthRate
from ..connections import getConnection


class Query(BaseQuery):

    growth_rates = List(
        GrowthRate,
        description="A list of growth rates.",
        name=String()
    )

    def resolve_growth_rates(self, info, **kwargs):
        q = models.GrowthRate.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs['name'])
        return q
