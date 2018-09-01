# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay
from django.db.models import Sum

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder
from ..relay_node import RelayNode
from ..loader_key import LoaderKey


class PokemonEncounter(ObjectType):
    """
    A list of encounters by version for a specific Location Area and Pokémon.
    """

    location_area_id = None
    location_area = Field(
        lazy_import("pokemon_graphql.location_area.types.LocationArea"),
        description="The location area the referenced Pokémon can be encountered in."
    )
    pokemon_id = None
    pokemon = Field(
       lazy_import('pokemon_graphql.pokemon.types.Pokemon'),
       description="The Pokémon being encountered."
    )
    version_details = List(
        lambda: VersionEncounterDetail,
        description="A list of versions and encounters with Pokémon that might happen in the referenced location area."
    )

    def resolve_location_area(self, info):
        return info.context.loaders.locationarea.load(self.location_area_id)

    def resolve_pokemon(self, info):
        return info.context.loaders.pokemon.load(self.pokemon_id)

    def resolve_version_details(self, info):
        key = LoaderKey(0,
            location_area_id=self.location_area_id,
            pokemon_id=self.pokemon_id
        )
        return info.context.loaders.encounters_by_locationarea_and_pokemon.load(key) \
            .then(lambda data: PokemonEncounter.get_version_details(self, data))

    @staticmethod
    def get_version_details(root, encounters):

        # Group encounters by version
        v_encounters = {}
        for e in encounters:
            if e.version_id not in v_encounters:
                v_encounters[e.version_id] = []
            v_encounters[e.version_id].append(e)

        version_details = []
        for version_id, enctrs in v_encounters.iteritems():
            ver_detail = VersionEncounterDetail()
            ver_detail.location_area_id = root.location_area_id
            ver_detail.pokemon_id = root.pokemon_id
            ver_detail.version_id = version_id
            version_details.append(ver_detail)

        return version_details


class PokemonEncounterConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonEncounter


class VersionEncounterDetail(ObjectType):
    """
    A list of encounters for a specific Location Area, Pokémon, and Version.
    """
    location_area_id = None
    pokemon_id = None
    max_chance = Int(description='The total sum of all encounter potential.')
    encounter_details = relay.ConnectionField(
        lazy_import('pokemon_graphql.encounter.types.EncounterConnection'),
        description='A list of encounters and their specifics.',
        where=Argument(lazy_import('pokemon_graphql.encounter.types.EncounterWhere')),
        order_by=Argument(List(
            lazy_import('pokemon_graphql.encounter.types.EncounterOrdering')
        ))
    )
    version_id = None
    version = Field(
        lazy_import('pokemon_graphql.version.types.Version'),
        description='The game version this encounter happens in.'
    )

    def resolve_max_chance(self, info):
        return models.Encounter.objects.filter(
            location_area_id=self.location_area_id,
            pokemon_id=self.pokemon_id,
            version_id=self.version_id
        ).aggregate(Sum("encounter_slot__rarity"))["encounter_slot__rarity__sum"]

    def resolve_version(self, info):
        return info.context.loaders.version.load(self.version_id)

    def resolve_encounter_details(self, info, **kwargs):
        from ..encounter.types import EncounterConnection, Encounter, EncounterWhere

        q = models.Encounter.objects.filter(
            location_area_id=self.location_area_id,
            pokemon_id=self.pokemon_id,
            version_id=self.version_id
        ).select_related('encounter_slot')
        q = EncounterWhere.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EncounterConnection, Encounter.fill, **kwargs)
