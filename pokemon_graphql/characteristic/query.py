# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import CharacteristicConnection, CharacteristicOrdering
from ..where import Where


class Query(BaseQuery):
    characteristics = relay.ConnectionField(
        CharacteristicConnection,
        description='A list of characteristics (e.g. "Loves to eat, Alert to sounds").',
        where=Argument(Where),
        order_by=List(CharacteristicOrdering)
    )

    def resolve_characteristics(self, info, **kwargs):
        q = models.Characteristic.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, CharacteristicConnection, **kwargs)
