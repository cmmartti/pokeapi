# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from ..where import Where
from .types import EncounterMethodConnection, EncounterMethodOrdering


class Query(BaseQuery):
    encounter_methods = relay.ConnectionField(
        lambda: EncounterMethodConnection,
        description="A list of methods by which a player might encounter Pokémon in the wild.",
        where=Argument(Where),
        order_by=Argument(List(lambda: EncounterMethodOrdering))
    )

    def resolve_encounter_methods(self, info, **kwargs):
        q = models.EncounterMethod.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EncounterMethodConnection, **kwargs)
