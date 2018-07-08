# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from .types import MoveBattleStyle


class Query(BaseQuery):

    move_battle_styles = List(
        MoveBattleStyle,
        description="A list of styles of moves when used in the Battle Palace.",
        name=String()
    )

    def resolve_move_battle_styles(self, info, **kwargs):
        q = models.MoveBattleStyle.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
