# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from ..where import Where


class Query(BaseQuery):
    encounter_methods = relay.ConnectionField(
        lambda: EncounterMethodConnection,
        description="A list of methods by which a player might encounter Pokémon in the wild.",
        where=Argument(Where),
        order_by=Argument(lambda: EncounterMethodOrder)
    )

    def resolve_encounter_methods(self, info, **kwargs):
        q = models.EncounterMethod.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EncounterMethodConnection, **kwargs)


from .types import EncounterMethodConnection, EncounterMethodOrder
