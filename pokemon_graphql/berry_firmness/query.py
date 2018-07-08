# -*- coding: utf-8 -*-
from graphene import List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import BerryFirmness


class Query(BaseQuery):

    berry_firmnesses = List(
        BerryFirmness,
        description="A list of berry firmnesses.",
        name=String()
    )

    def resolve_berry_firmnesses(self, info, **kwargs):
        q = models.BerryFirmness.objects.all()
        if "id" in kwargs: q = q.filter(name=kwargs['name'])
        return q
