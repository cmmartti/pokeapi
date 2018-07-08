# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from .types import MoveAilment


class Query(BaseQuery):

    move_ailments = List(
        MoveAilment,
        description="A list of move ailments (status conditions) caused by moves used during battle.",
        name=String()
    )

    def resolve_move_ailments(self, info, **kwargs):
        q = models.MoveMetaAilment.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
