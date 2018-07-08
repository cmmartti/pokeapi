# -*- coding: utf-8 -*-
from graphene import *

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder, BaseName
from ..relay_node import RelayNode
from ..field import TranslationList


class EncounterCondition(ObjectType):
    """
    Conditions which affect what pokemon might appear in the wild, e.g., day or night.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: EncounterConditionName,
        description="The name of this encounter condition listed in different languages."
    )
    values = List(
        lazy_import("pokemon_graphql.encounter_condition_value.types.EncounterConditionValue"),
        description="A list of possible values for this encounter condition."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.encountercondition_names.load(key)

    def resolve_values(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.encountercondition_values.load(key)


    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encountercondition.load(id)


class EncounterConditionName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encounterconditionname.load(id)
