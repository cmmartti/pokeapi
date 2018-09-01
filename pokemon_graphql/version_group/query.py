# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import VersionGroupConnection, VersionGroupOrdering
from ..where import Where


class Query(BaseQuery):
    version_groups = relay.ConnectionField(
        VersionGroupConnection,
        description="A list of version groups (highly similar versions of the games).",
        where=Argument(Where),
        order_by=Argument(List(VersionGroupOrdering))
    )

    def resolve_version_groups(self, info, **kwargs):
        q = models.VersionGroup.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, VersionGroupConnection, **kwargs)
