# -*- coding: utf-8 -*-
from graphene import Int, String, Boolean, Field, List, ObjectType, Enum, relay, Argument
from graphene import lazy_import

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from .id import VersionEncounterDetailID


class VersionEncounterDetail(ObjectType):
    """
    A list of encounters for a specific Location Area, Pokémon, and Version.
    """
    location_area_id = None
    pokemon_id = None
    maxChance = Int(description='The total percentage of all encounter potential.')
    encounter_details = relay.ConnectionField(
        lazy_import('pokemon_graphql.encounter.types.EncounterConnection'),
        description='A list of encounters and their specifics.',
        where=Argument(lazy_import('pokemon_graphql.encounter.types.EncounterWhere')),
        order_by=Argument(lazy_import('pokemon_graphql.encounter.types.EncounterOrder'))
    )
    version_id = None
    version = Field(
        lazy_import('pokemon_graphql.version.types.Version'),
        description='The game version this encounter happens in.')

    def resolve_version(self, info):
        return info.context.loaders.version.load(self.version_id)

    def resolve_encounter_details(self, info, **kwargs):
        from ..encounter.types import EncounterConnection, Encounter

        q = models.Encounter.objects.all()
        q = q.filter(location_area_id=self.location_area_id)
        q = q.filter(pokemon_id=self.pokemon_id)
        q = q.filter(version_id=self.version_id)
        q = q.select_related('encounter_slot')
        return getConnection(q, EncounterConnection, Encounter.fill, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, encoded_id):

        # There is no model counterpart for this schema type, hence the composite ID
        id = VersionEncounterDetailID.decode(encoded_id)

        q = models.Encounter.objects.all()
        q = q.filter(location_area_id=id.location_area_id)
        q = q.filter(pokemon_id=id.pokemon_id)
        q = q.filter(version_id=id.version_id)
        q = q.select_related('encounter_slot')
        return cls.fill(q, id)

    @classmethod
    def fill(cls, data, id):

        obj = cls(id=id)
        obj.location_area_id = id.location_area_id
        obj.pokemon_id = id.pokemon_id
        obj.version_id = id.version_id

        maxChance = 0
        for encounter in data:
            maxChance += encounter.encounter_slot.rarity
        obj.maxChance = maxChance

        return obj
