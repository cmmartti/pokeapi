# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder
from ..relay_node import RelayNode
from ..where import BaseWhere


class Encounter(ObjectType):
    '''
    An encounter is a set of conditions that must be met in order to meet a particular Pokémon in a particular game version, and the likelihood that the encounter will occur if the conditions are met.
    '''

    chance = Int(description='The percent chance that this encounter will occur.')
    condition_values = List(
        lazy_import('pokemon_graphql.encounter_condition_value.types.EncounterConditionValue'),
        description='A list of condition values that must be in effect for this encounter to occur.'
    )
    location_area_id = None
    location_area = Field(
        lazy_import("pokemon_graphql.location_area.types.LocationArea"),
        description="The location area this encounter occurs in."
    )
    max_level = Int(description='The highest level the Pokémon can be encountered at.')
    encounter_method_id = None
    method = Field(
        lazy_import("pokemon_graphql.encounter_method.types.EncounterMethod"),
        description='The method by which this encounter happens.'
    )
    min_level = Int(description='The lowest level the Pokémon can be encountered at.')
    pokemon_id = None
    pokemon = Field(
        lazy_import("pokemon_graphql.pokemon.types.Pokemon"),
        description="The Pokémon that is encountered."
    )
    version_id = None
    version = Field(
        lazy_import("pokemon_graphql.version.types.Version"),
        description="The game version this encounter occurs in."
    )

    def resolve_condition_values(self, info):
        key = LoaderKey(self.id)
        return info.context.loaders.encounterconditionvalues_by_encounter.load(key)

    def resolve_location_area(self, info):
        return info.context.loaders.locationarea.load(self.location_area_id)

    def resolve_pokemon(self, info):
        return info.context.loaders.pokemon.load(self.pokemon_id)

    def resolve_method(self, info):
        return info.context.loaders.encountermethod.load(self.encounter_method_id)

    def resolve_version(self, info):
        return info.context.loaders.version.load(self.version_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encounter_with_encounterslot.load(id).then(cls.fill)

    @classmethod
    def fill(cls, encounter):
        assert isinstance(encounter, models.Encounter)
        slot = encounter.encounter_slot

        obj = cls(id=encounter.id)
        obj.chance = slot.rarity
        obj.encounter_method_id = slot.encounter_method_id
        obj.max_level = encounter.max_level
        obj.min_level = encounter.min_level
        obj.location_area_id = encounter.location_area_id
        obj.pokemon_id = encounter.pokemon_id
        obj.version_id = encounter.version_id

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


class EncounterWhere(BaseWhere):
    """Filtering options for encounter connections."""
    max_level__gt = Int(description="maxLevel is greater than ___.")
    min_level__gt = Int(description="minLevel is greater than ___.")
    encounter_method_id = ID(
        name="method_ID",
        description="The global ID of an encounter method."
    )
    location_area_id = ID(
        name="locationArea_ID",
        description="The global ID of a location area an encounter occurs in."
    )
    version_id = ID(
        name="version_ID",
        description="The global ID of a game version an encounter occurs in."
    )

    @classmethod
    def apply(cls, query_set, **where):

        encounter_method_id = where.pop("encounter_method_id", None)
        if encounter_method_id:
            id = cls.get_id(encounter_method_id, "EncounterMethod", "method_ID")
            query_set = query_set.filter(encounter_slot__encounter_method_id=id)

        location_area_id = where.pop("location_area_id", None)
        if location_area_id:
            id = cls.get_id(location_area_id, "LocationArea", "locationArea_ID")
            query_set = query_set.filter(location_area_id=id)

        version_id = where.pop("version_id", None)
        if version_id:
            id = cls.get_id(version_id, "Version", "version_ID")
            query_set = query_set.filter(version_id=id)

        return super(EncounterWhere, cls).apply(query_set, **where)
