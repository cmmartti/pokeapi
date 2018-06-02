# -*- coding: utf-8 -*-
from graphene import Int, String, Boolean, Field, List, ObjectType, Enum, relay
from graphene import lazy_import

from ..base import BaseConnection, BaseOrder
from ..loader_key import LoaderKey
from ..relay_node import RelayNode


class VersionGroup(ObjectType):
    """Version groups categorize highly similar versions of the games."""

    name = String(description="The name of this resource.")
    order = Int(description="Order for sorting. Almost by date of release, except similar versions are grouped together.")
    generation_id = None
    generation = Field(
        lazy_import('pokemon_graphql.generation.types.Generation'),
        description="The generation this version was introduced in."
    )
    versions = List(
        lazy_import('pokemon_graphql.version.types.Version'),
        description="The versions this version group owns."
    )

    def resolve_generation(self, info):
        return info.context.loaders.generation.load(self.generation_id)

    def resolve_versions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versions_by_versiongroup.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.versiongroup.load(id)


class VersionGroupConnection(BaseConnection, relay.Connection):
    class Meta:
        node = VersionGroup


class VersionGroupOrderField(Enum):
    """Properties by which version group connections can be ordered."""
    ORDER = "order"
    NAME = "name"

    @property
    def description(self):
        if self == VersionGroupOrderField.ORDER:
            return "Order version groups by standard order."
        if self == VersionGroupOrderField.NAME:
            return "Order version groups by name."


class VersionGroupOrder(BaseOrder):
    """Ordering options for version group connections."""
    field = VersionGroupOrderField(
        description="The field to order version groups by.",
        required=True
    )
