# -*- coding: utf-8 -*-
from graphene import relay, List, String

from pokemon_v2 import models
from ..base import BaseQuery
from .types import MoveLearnMethod


class Query(BaseQuery):

    move_learn_methods = List(
        MoveLearnMethod,
        description="A list of methods by which Pokémon can learn moves.",
        name=String()
    )

    def resolve_move_learn_methods(self, info, **kwargs):
        q = models.MoveLearnMethod.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return q
