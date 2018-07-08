# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import BaseWhere


class Machine(ObjectType):
    """
    Machines are the representation of items that teach moves to Pokémon. They vary from version to version, so it is not certain that one specific TM (Technical Machine) or HM (Hidden Machine) number corresponds to a single Machine.
    """

    item_id = None
    item = Field(
        lazy_import("pokemon_graphql.item.types.Item"),
        description="The TM or HM item that corresponds to this machine."
    )
    move_id = None
    move = Field(
        lazy_import("pokemon_graphql.move.types.Move"),
        description="The move that is taught by this machine."
    )
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group that this machine applies to."
    )

    def resolve_item(self, info):
        from ..item_interface.connection import get_item_node

        return info.context.loaders.item.load(self.item_id).then(get_item_node)

    def resolve_move(self, info):
        return info.context.loaders.move.load(self.move_id)

    def resolve_version_group(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.machine.load(id)


class MachineConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Machine


class MachineOrderField(Enum):
    """Properties by which machine connections can be ordered."""

    NAME = "name"

    @property
    def description(self):
        if self == MachineOrderField.NAME:
            return "Order machines by name."


class MachineOrder(BaseOrder):
    """Ordering options for machine connections."""
    field = MachineOrderField(
        description="The field to order machines by.",
        required=True
    )


class MachineWhere(BaseWhere):
    """Filtering options for machine connections."""

    version_group_id = ID(
        name="versionGroup_ID",
        description="Filter by the global ID of a resource."
    )

    @classmethod
    def apply(cls, query_set, **where):

        version_group_id = where.pop("version_group_id", None)
        if version_group_id:
            id = cls.get_id(version_group_id, "Version", "versionGroup_ID")
            query_set = query_set.filter(version_group_id=id)

        return super(MachineWhere, cls).apply(query_set, **where)
