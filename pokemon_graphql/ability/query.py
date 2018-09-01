# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import AbilityConnection, AbilityOrdering
from ..where import Where


class Query(BaseQuery):
    abilities = relay.ConnectionField(
        AbilityConnection,
        description="A list of abilities Pokémon can have.",
        where=Argument(Where),
        order_by=List(AbilityOrdering)
    )

    def resolve_abilities(self, info, **kwargs):
        q = models.Ability.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, AbilityConnection, **kwargs)
