# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder, BaseName
from ..relay_node import RelayNode
from ..field import TranslationList


class EncounterMethod(ObjectType):
    """
    Methods by which the player might encounter Pokémon in the wild, e.g., walking in tall grass. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Wild_Pok%C3%A9mon) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: EncounterMethodName,
        description="The name of this encounter method listed in different languages."
    )
    order = Int(description="A good value for sorting.")

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.encountermethod_names.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encountermethod.load(id)


class EncounterMethodConnection(BaseConnection, relay.Connection):
    class Meta:
        node = EncounterMethod


class EncounterMethodOrdering(BaseOrder):
    sort = InputField(
        Enum('EncounterMethodSort', [("ORDER", "order"), ("NAME", "name")]),
        description="The field to sort by."
    )



class EncounterMethodName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encountermethodname.load(id)
