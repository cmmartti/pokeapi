# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..egg_group.types import EggGroupConnection, EggGroupOrdering
from ..connections import getConnection
from ..where import Where


class Query(BaseQuery):

    egg_groups = relay.ConnectionField(
        EggGroupConnection,
        description="A list of egg groups, categories that determine which Pokémon are able to interbreed.",
        where=Argument(Where),
        order_by=Argument(List(EggGroupOrdering))
    )

    def resolve_egg_groups(self, info, **kwargs):
        q = models.EggGroup.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EggGroupConnection, **kwargs)
