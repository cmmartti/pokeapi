# -*- coding: utf-8 -*-
from graphene import *

from ..base import BaseEffect, BaseFlavorText
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class ContestEffect(ObjectType):
    """
    Contest effects refer to the effects of moves when used in contests.
    """

    appeal = Int(description="The base number of hearts the user of this move gets.")
    jam = Int(description="The base number of hearts the user's opponent loses.")
    effect_entries = TranslationList(
        lambda: ContestEffectEffectText,
        description="The result of this contest effect listed in different languages."
    )
    flavor_text_entries = TranslationList(
        lambda: ContestEffectFlavorText,
        description="The flavor text of this contest effect listed in different languages."
    )

    def resolve_effect_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.contesteffect_effectentries.load(key)

    def resolve_flavor_text_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.contesteffect_flavortextentries.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.contesteffect.load(id)


class ContestEffectEffectText(BaseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.contesteffecteffect.load(id)


class ContestEffectFlavorText(BaseFlavorText):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.contesteffectflavortext.load(id)
