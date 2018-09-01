# -*- coding: utf-8 -*-
from graphene import relay, Argument, List, Field, String
from django.core.exceptions import ObjectDoesNotExist

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import (
    TypeConnection as Connection,
    TypeOrdering as Ordering,
    Type
)
from ..where import Where


class Query(BaseQuery):
    types = relay.ConnectionField(
        Connection,
        description="A list of types Pokémon and moves can have.",
        where=Argument(Where),
        order_by=List(Ordering)
    )

    def resolve_types(self, info, **kwargs):
        q = models.Type.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, Connection, **kwargs)

    type = Field(Type, name=String())

    def resolve_type(self, info, **kwargs):
        if "name" in kwargs:
            try:
                return models.Type.objects.get(name=kwargs["name"])
            except ObjectDoesNotExist:
                return None;
        else: return None;
