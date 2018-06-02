# -*- coding: utf-8 -*-
from graphene import String, Int, Field, List, ObjectType, Enum, relay
from graphene import lazy_import

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder, BaseName
from ..relay_node import RelayNode
from ..field import TranslationList


class EncounterMethodRate(ObjectType):
    location_area_id = None
    encounter_method_id = None
    encounter_method = Field(
        lazy_import('pokemon_graphql.encounter_method.types.EncounterMethod'),
        description="The method in which Pokémon may be encountered in an area."
    )
    version_details = List(
        lambda: EncounterVersionDetails,
        description="The chance of the encounter to occur on a version of the game."
    )

    def resolve_encounter_method(self, info):
        return info.context.loaders.encountermethod.load(self.encounter_method_id)

    def resolve_version_details(self, info, **kwargs):
        key = LoaderKey(self.location_area_id, **kwargs)
        return info.context.loaders.locationareaencounterrates_by_locationarea.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationareaencounterrate.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id)
        obj.location_area_id = data.location_area_id
        obj.encounter_method_id = data.encounter_method_id
        return obj


class EncounterVersionDetails(ObjectType):
    rate = Int(description="The chance of an encounter to occur.")
    version_id = None
    version = Field(
        lazy_import('pokemon_graphql.version.types.Version'),
        description="The version of the game in which the encounter can occur with the given chance."
    )

    def resolve_version(self, info, **kwargs):
        return info.context.loaders.version.load(self.version_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationareaencounterrate.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id)
        obj.location_area_id = data.location_area_id
        obj.encounter_method_id = data.encounter_method_id
        return obj
