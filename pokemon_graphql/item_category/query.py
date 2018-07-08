# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from .types import ItemCategory


class Query(BaseQuery):

    item_categories = List(
        ItemCategory,
        description="A list of item categories.",
        name=String()
    )

    def resolve_item_categories(self, info, **kwargs):
        q = models.ItemCategory.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
