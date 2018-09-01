# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import (
    LanguageConnection as Connection,
    LanguageOrdering as Ordering,
    LanguageWhere as Where,
)


class Query(BaseQuery):
    languages = relay.ConnectionField(
        Connection,
        description="A list of languages used for translations of resource information.",
        where=Argument(Where),
        order_by=List(Ordering)
    )

    def resolve_languages(self, info, **kwargs):
        q = models.Language.objects.all()
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, Connection, **kwargs)
