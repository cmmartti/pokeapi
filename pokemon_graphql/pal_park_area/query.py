# -*- coding: utf-8 -*-
from graphene import List, Argument, String

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import PalParkArea
from ..where import Where


class Query(BaseQuery):

    pal_park_areas = List(
        PalParkArea,
        description="A list of areas in Pal Park.",
        name=String()
    )

    def resolve_pal_park_areas(self, info, **kwargs):
        q = models.PalParkArea.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs['name'])
        return q
