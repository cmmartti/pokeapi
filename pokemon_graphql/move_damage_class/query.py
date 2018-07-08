# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from .types import MoveDamageClass


class Query(BaseQuery):

    move_damage_classes = List(
        MoveDamageClass,
        description="A list of damage classes that moves can have.",
        name=String()
    )

    def resolve_move_damage_classes(self, info, **kwargs):
        q = models.MoveDamageClass.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
