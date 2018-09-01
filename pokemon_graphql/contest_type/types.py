# -*- coding: utf-8 -*-
from graphene import *

from ..base import BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class ContestType(ObjectType):
    """
    Contest types are categories judges used to weigh a Pokémon's condition in Pokémon contests. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Contest_condition) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: ContestTypeName,
        description="The name of this contest type listed in different languages."
    )
    berry_flavor = Field(
        lazy_import("pokemon_graphql.berry_flavor.types.BerryFlavor"),
        description="The berry flavor that correlates with this contest type."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.contesttype_names.load(key)

    def resolve_berry_flavor(self, info):
        return info.context.loaders.berryflavor_by_contesttype.load(self.id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.contesttype.load(id)


class ContestTypeName(BaseName):
    color = String(description="The color associated with this contest's name.")

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.contesttypename.load(id)
