# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from .types import MoveTarget


class Query(BaseQuery):

    move_targets = List(
        MoveTarget,
        description="A list of targets that moves can be directed at during battle.",
        name=String()
    )

    def resolve_move_targets(self, info, **kwargs):
        q = models.MoveTarget.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
