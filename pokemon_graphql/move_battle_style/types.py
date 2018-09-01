# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from ..base import BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class MoveBattleStyle(ObjectType):
    """
    Styles of moves when used in the Battle Palace. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Battle_Frontier_(Generation_III)) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: MoveBattleStyleName,
        description="The name of this move battle style listed in different languages."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movebattlestyle_names.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movebattlestyle.load(id)


class MoveBattleStyleName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movebattlestylename.load(id)
