# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import LocationAreaConnection, LocationAreaOrder
from ..where import Where


class Query(BaseQuery):
    location_areas = relay.ConnectionField(
        LocationAreaConnection,
        description="A list of location areas that can be visited within games.",
        where=Argument(Where), order_by=Argument(LocationAreaOrder)
    )

    def resolve_location_areas(self, info, **kwargs):
        q = models.LocationArea.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, LocationAreaConnection, **kwargs)
