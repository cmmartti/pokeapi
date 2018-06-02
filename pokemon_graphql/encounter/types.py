# -*- coding: utf-8 -*-
from graphene import Int, List, Field, ObjectType, Enum, InputObjectType, relay
from graphene import lazy_import

from pokemon_v2 import models
from ..base import BaseConnection, BaseOrder
from ..relay_node import RelayNode


class Encounter(ObjectType):
    '''
    An encounter is a set of conditions that must be met in order to meet a particular Pokémon, and the likelihood that the encounter will occur if the conditions are met.
    '''

    chance = Int(description='The percent chance that this encounter will occur.')
    # condition_values = List(
    #     lazy_import('pokemon_graphql.encounter_condition_value.types.EncounterConditionValue'),
    #     description='A list of condition values that must be in effect for this encounter to occur.'
    # )
    max_level = Int(description='The highest level the Pokémon can be encountered at.')
    encounter_method_id = None
    method = Field(
        lazy_import("pokemon_graphql.encounter_method.types.EncounterMethod"),
        description='The method by which this encounter happens.'
    )
    min_level = Int(description='The lowest level the Pokémon can be encountered at.')

    def resolve_condition_values(self, info):
        return info.context.loaders.encounterconditionvalues_by_encounter(self.id)

    def resolve_method(self, info):
        return info.context.loaders.encountermethod.load(self.encounter_method_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encounter_with_encounterslot.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        assert isinstance(data, models.Encounter)
        slot = data.encounter_slot
        obj = cls(id=data.id)
        obj.chance = slot.rarity
        obj.encounter_method_id = slot.encounter_method_id
        obj.max_level = data.max_level
        obj.min_level = data.min_level
        return obj


class EncounterConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Encounter


class EncounterOrderField(Enum):
    """Properties by which encounter connections can be ordered."""
    CHANCE = "chance"
    MAX_LEVEL = "max_level"
    MIN_LEVEL = "min_level"

    @property
    def description(self):
        if self == EncounterOrderField.CHANCE:
            return "Order encounters by the percent chance that each will occur."
        if self == EncounterOrderField.MAX_LEVEL:
            return "Order encounters by the highest level the Pokémon can be encountered at."
        if self == EncounterOrderField.MIN_LEVEL:
            return "Order encounters by the lowest level the Pokémon can be encountered at."


class EncounterOrder(BaseOrder):
    """Ordering options for encounter connections."""
    field = EncounterOrderField(
        description="The field to order encounters by.",
        required=True
    )


class EncounterWhere(InputObjectType):
    """Filtering options for encounter connections."""
    max_level__gt = Int(description="maxLevel is greater than ___.")
    min_level__lt = Int(description="maxLevel is less than ___.")
