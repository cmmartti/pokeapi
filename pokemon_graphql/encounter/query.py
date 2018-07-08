# -*- coding: utf-8 -*-
from graphene import Argument, relay

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import Encounter, EncounterConnection, EncounterWhere, EncounterOrder


class Query(BaseQuery):
    encounters = relay.ConnectionField(
        EncounterConnection,
        description="A list of situations in which a player might encounter Pokémon in the wild.",
        where=Argument(EncounterWhere),
        order_by=Argument(EncounterOrder)
    )

    def resolve_encounters(self, info, **kwargs):
        q = models.Encounter.objects.all().select_related("encounter_slot")
        q = EncounterWhere.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EncounterConnection, Encounter.fill, **kwargs)
