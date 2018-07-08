# -*- coding: utf-8 -*-
from graphene import List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import BerryFlavor


class Query(BaseQuery):

    berry_flavors = List(
        BerryFlavor,
        description="A list of berry flavors.",
        name=String()
    )

    def resolve_berry_flavors(self, info, **kwargs):
        q = models.BerryFlavor.objects.all()
        if "id" in kwargs: q = q.filter(name=kwargs['name'])
        return q
