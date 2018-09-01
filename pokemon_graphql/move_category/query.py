# -*- coding: utf-8 -*-
from graphene import relay, List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import MoveCategory


class Query(BaseQuery):

    move_categories = List(
        MoveCategory,
        description="A list of general categories that group move effects.",
        name=String()
    )

    def resolve_move_categories(self, info, **kwargs):
        q = models.MoveMetaCategory.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
