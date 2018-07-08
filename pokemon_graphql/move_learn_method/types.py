# -*- coding: utf-8 -*-
from graphene import Int, String, Boolean, Field, List, ObjectType, Enum, relay, Argument, InputObjectType, ID
from graphene import lazy_import

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class MoveLearnMethod(ObjectType):
    """
    Methods by which Pokémon can learn moves.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: MoveLearnMethodName,
        description="The name of this move learn method listed in different languages."
    )
    descriptions = TranslationList(
        lambda: MoveLearnMethodDescription,
        description="The description of this move learn method listed in different languages."
    )
    version_groups = List(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="A list of version groups where moves can be learned through this method."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movelearnmethod_names.load(key)

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.movelearnmethod_descriptions.load(key)

    def resolve_version_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versiongroups_by_movelearnmethod.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movelearnmethod.load(id)


class MoveLearnMethodName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movelearnmethodname.load(id)


class MoveLearnMethodDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movelearnmethoddescription.load(id)
