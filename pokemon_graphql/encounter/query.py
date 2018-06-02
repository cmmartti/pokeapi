# -*- coding: utf-8 -*-
from graphene import Argument, relay

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import EncounterConnection, EncounterWhere, EncounterOrder


class Query(BaseQuery):
    pass
    # encounters = relay.ConnectionField(
    #     EncounterConnection,
    #     description="A list of situations in which a player might encounter Pokémon in the wild.",
    #     where=Argument(EncounterWhere), order_by=Argument(EncounterOrder)
    # )

    # def resolve_encounters(self, info, **kwargs):
    #     q = models.Encounter.objects.all()
    #     return getConnection(q, EncounterConnection, **kwargs)
