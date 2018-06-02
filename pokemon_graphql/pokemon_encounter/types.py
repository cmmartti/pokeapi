# -*- coding: utf-8 -*-
from graphene import Int, List, Field, ObjectType, relay
from graphene import lazy_import

from pokemon_v2 import models
from ..base import BaseConnection, BaseOrder
from ..relay_node import RelayNode
from .id import PokemonEncounterID


class PokemonEncounter(ObjectType):
    """
    A list of encouters by version for a specific Location Area and Pokémon.
    """

    location_area_id = None
    pokemon_id = Int()
    # pokemon = Field(
    #    lazy_import('pokemon_graphql.pokemon.types.Pokemon'),
    #    description="The Pokémon being encountered."
    # )
    version_details = List(
        lazy_import('pokemon_graphql.version_encounter_detail.types.VersionEncounterDetail'),
        description="A list of versions and encounters with Pokémon that might happen in the referenced location area."
    )

    def resolve_pokemon(self, info):
        return info.context.loaders.pokemon.load(self.pokemon_id)

    def resolve_version_details(self, info):
        from ..version_encounter_detail.types import VersionEncounterDetail
        from ..version_encounter_detail.id import VersionEncounterDetailID

        encounters = models.Encounter.objects.all()
        encounters = encounters.select_related('encounter_slot')
        encounters = encounters.filter(location_area_id=self.location_area_id)
        encounters = encounters.filter(pokemon_id=self.pokemon_id)

        # Group encounters by version
        v_encounters = {}
        for e in encounters:
            if e.version_id not in v_encounters:
                v_encounters[e.version_id] = []
            v_encounters[e.version_id].append(e)

        version_details = []
        for v_id, enctrs in v_encounters.iteritems():
            id = VersionEncounterDetailID(self.location_area_id, self.pokemon_id, v_id)
            version_detail = VersionEncounterDetail.fill(enctrs, id)
            version_details.append(version_detail)
        return version_details

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        # No database calls here because all scalar data is encoded in the composite ID
        return cls.fill(PokemonEncounterID.decode(id))

    @classmethod
    def fill(cls, id):
        obj = cls(id=id)
        obj.location_area_id = id.location_area_id
        obj.pokemon_id = id.pokemon_id
        return obj


class PokemonEncounterConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonEncounter
