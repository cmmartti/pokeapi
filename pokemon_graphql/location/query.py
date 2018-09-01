# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import LocationConnection, LocationOrdering
from ..where import Where


class Query(BaseQuery):
    locations = relay.ConnectionField(
        LocationConnection,
        description="A list of locations that can be visited within games.",
        where=Argument(Where),
        order_by=Argument(List(LocationOrdering))
    )

    def resolve_locations(self, info, **kwargs):
        q = models.Location.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, LocationConnection, **kwargs)
