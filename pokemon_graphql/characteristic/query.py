# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import CharacteristicConnection, CharacteristicOrder
from ..where import Where


class Query(BaseQuery):
    characteristics = relay.ConnectionField(
        CharacteristicConnection,
        description='A list of characteristics (e.g. "Loves to eat, Alert to sounds").',
        where=Argument(Where),
        order_by=Argument(CharacteristicOrder)
    )

    def resolve_characteristics(self, info, **kwargs):
        q = models.Characteristic.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, CharacteristicConnection, **kwargs)
