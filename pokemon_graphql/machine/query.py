# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import MachineConnection, MachineOrdering, MachineWhere


class Query(BaseQuery):

    machines = relay.ConnectionField(
        MachineConnection,
        description="A list of machines that teach moves to Pokémon.",
        where=Argument(MachineWhere),
        order_by=Argument(List(MachineOrdering))
    )

    def resolve_machines(self, info, **kwargs):
        q = models.Machine.objects.all()
        q = MachineWhere.apply(q, **kwargs.get("where", {}))
        return getConnection(q, MachineConnection, **kwargs)
