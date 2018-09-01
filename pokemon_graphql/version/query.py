# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import VersionConnection, VersionOrdering
from ..where import Where


class Query(BaseQuery):
    versions = relay.ConnectionField(
        VersionConnection,
        description="A list of versions of the games, e.g., Red, Blue or Yellow.",
        where=Argument(Where),
        order_by=Argument(List(VersionOrdering))
    )

    def resolve_versions(self, info, **kwargs):
        q = models.Version.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, VersionConnection, **kwargs)
