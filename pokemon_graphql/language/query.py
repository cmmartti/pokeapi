# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import LanguageConnection, LanguageOrder
from ..where import Where


class Query(BaseQuery):
    languages = relay.ConnectionField(
        LanguageConnection,
        description="A list of languages used for translations of resource information.",
        where=Argument(Where), order_by=Argument(LanguageOrder)
    )

    def resolve_languages(self, info, **kwargs):
        q = models.Language.objects.all()
        return getConnection(q, LanguageConnection, **kwargs)
