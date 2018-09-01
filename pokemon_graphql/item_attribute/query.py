# -*- coding: utf-8 -*-
from graphene import relay, List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import ItemAttribute


class Query(BaseQuery):

    item_attributes = List(
        ItemAttribute,
        description="A list of item attributes.",
        name=String()
    )

    def resolve_item_attributes(self, info, **kwargs):
        q = models.ItemAttribute.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
