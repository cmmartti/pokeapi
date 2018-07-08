# -*- coding: utf-8 -*-
from graphene import List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import Gender


class Query(BaseQuery):

    genders = List(
        Gender,
        description="A list of genders.",
        name=String()
    )

    def resolve_genders(self, info, **kwargs):
        q = models.Gender.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs['name'])
        return q
