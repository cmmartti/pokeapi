# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from .types import ItemPocket


class Query(BaseQuery):

    item_pockets = List(
        ItemPocket,
        description="A list of item categories.",
        name=String()
    )

    def resolve_item_pockets(self, info, **kwargs):
        q = models.ItemPocket.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
