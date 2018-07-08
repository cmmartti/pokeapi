# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import MachineConnection, MachineOrder, MachineWhere


class Query(BaseQuery):

    machines = relay.ConnectionField(
        MachineConnection,
        description="A list of machines that teach moves to Pokémon.",
        order_by=Argument(MachineOrder),
        where=Argument(MachineWhere)
    )

    def resolve_machines(self, info, **kwargs):
        q = models.Machine.objects.all()
        q = MachineWhere.apply(q, **kwargs.get("where", {}))
        return getConnection(q, MachineConnection, **kwargs)
