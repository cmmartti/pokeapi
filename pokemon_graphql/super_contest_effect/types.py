# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay
from django.db.models import Prefetch

from pokemon_v2 import models
from ..connections import getPage
from ..base import BaseFlavorText
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class SuperContestEffect(ObjectType):
    """
    Super contest effects refer to the effects of moves when used in super contests.
    """

    appeal = Int(description="The base number of hearts the user of this move gets.")
    flavor_text_entries = TranslationList(
        lambda: SuperContestEffectFlavorText,
        description="The flavor text of this contest effect listed in different languages."
    )
    moves = List(
        lazy_import("pokemon_graphql.move.types.Move"),
        description="A list of moves that have the effect when used in super contests."
    )

    def resolve_flavor_text_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.supercontesteffect_flavortextentries.load(key)

    def resolve_moves(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.supercontesteffect_moves.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.supercontesteffect.load(id)


class SuperContestEffectFlavorText(BaseFlavorText):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.supercontesteffectflavortext.load(id)
