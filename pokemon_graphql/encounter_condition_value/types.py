# -*- coding: utf-8 -*-
from graphene import *

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder, BaseName
from ..relay_node import RelayNode
from ..field import TranslationList


class EncounterConditionValue(ObjectType):
    """
    Encounter condition values are the various states that an encounter condition can have, i.e., time of day can be either day or night.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: EncounterConditionValueName,
        description="The name of this encounter condition value listed in different languages."
    )
    encounter_condition_id = None
    condition = Field(
        lazy_import("pokemon_graphql.encounter_condition.types.EncounterCondition"),
        description="The condition this encounter condition value pertains to."
    )
    is_default = Boolean(
        description="Whether or not this is the default condition value."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.encounterconditionvalue_names.load(key)

    def resolve_condition(self, info):
        return info.context.loaders.encountercondition.load(self.encounter_condition_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encounterconditionvalue.load(id)


class EncounterConditionValueName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encounterconditionvaluename.load(id)
