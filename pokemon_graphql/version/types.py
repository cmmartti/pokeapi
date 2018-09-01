# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class Version(ObjectType):
    """Versions of the games, e.g., Red, Blue or Yellow."""

    name = String(description="The name of this resource.")
    version_group_id = None
    names = TranslationList(
        lambda: VersionName,
        description="The name of this version listed in different languages."
    )
    version_group = Field(
        lazy_import('pokemon_graphql.version_group.types.VersionGroup'),
        description="The version group this version belongs to."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.version_names.load(key)

    def resolve_version_group(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.version.load(id)


class VersionConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Version


class VersionName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.versionname.load(id)


class VersionOrdering(BaseOrder):
    sort = InputField(
        Enum('VersionSort', [("NAME", "name")]),
        description="The field to sort by."
    )
