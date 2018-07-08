# -*- coding: utf-8 -*-
from graphene import List, Argument, String

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from ..stat.types import Stat
from ..where import Where


class Query(BaseQuery):
    stats = List(
        Stat,
        description="A list of stats that determine certain aspects of battle.",
        name=String()
    )

    def resolve_stats(self, info, **kwargs):
        q = models.Stat.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
