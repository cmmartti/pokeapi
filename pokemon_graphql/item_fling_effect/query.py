# -*- coding: utf-8 -*-
from graphene import relay, List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import ItemFlingEffect


class Query(BaseQuery):

    item_fling_effects = List(
        ItemFlingEffect,
        description="A list of effects of the move \"Fling\" when used with different items.",
        name=String()
    )

    def resolve_item_fling_effects(self, info, **kwargs):
        q = models.ItemFlingEffect.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
