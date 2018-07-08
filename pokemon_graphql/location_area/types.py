# -*- coding: utf-8 -*-
from graphene import String, Int, Boolean, Field, List, ObjectType, Enum, relay
from graphene import lazy_import

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


ROOT = "pokemon_graphql."


class LocationArea(ObjectType):
    '''
    Location areas are sections of areas, such as floors in a building or cave. Each area has its own set of possible Pokémon encounters.
    '''

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: LocationAreaName,
        description="The name of this location area listed in different languages."
    )
    game_index = Int(description="The internal id of an API resource within game data.")
    location_id = None
    location = Field(
        lazy_import(ROOT + 'location.types.Location'),
        description="The location this area can be found in"
    )
    encounter_method_rates = List(
        lazy_import(ROOT + 'encounter_method_rate.types.EncounterMethodRate'),
        description="A list of methods in which Pokémon may be encountered in this area and how likely the method will occur depending on the version of the game."
    )
    pokemon_encounters = relay.ConnectionField(
        lazy_import(ROOT + 'pokemon_encounter.types.PokemonEncounterConnection'),
        description="A list of Pokémon encounters for this location area."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.locationarea_names.load(key)

    def resolve_location(self, info, **kwargs):
        return info.context.loaders.location.load(self.location_id)

    def resolve_encounter_method_rates(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.locationareaencounterrates_by_locationarea.load(key)

    def resolve_pokemon_encounters(self, info, **kwargs):
        from ..pokemon_encounter.types import PokemonEncounter, PokemonEncounterConnection
        from ..pokemon_encounter.id import PokemonEncounterID

        q = models.Pokemon.objects.all()
        q = q.filter(encounter__location_area_id=self.id).distinct()
        return getConnection(
            q, PokemonEncounterConnection,
            lambda data: LocationArea.get_pkmn_encounter(self, data),
            **kwargs
        )

    @staticmethod
    def get_pkmn_encounter(self, pokemon):
        from ..pokemon_encounter.types import PokemonEncounter

        pkmn_encounter = PokemonEncounter()
        pkmn_encounter.location_area_id = self.id
        pkmn_encounter.pokemon_id = pokemon.id
        return pkmn_encounter

    class Meta:
        interfaces = (RelayNode, )


    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationarea.load(id)


class LocationAreaConnection(BaseConnection, relay.Connection):
    class Meta:
        node = LocationArea


class LocationAreaOrderField(Enum):
    """Properties by which location area connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == LocationAreaOrderField.NAME:
            return "Order location areas by name."


class LocationAreaOrder(BaseOrder):
    """Ordering options for location area connections."""

    field = LocationAreaOrderField(
        description="The field to order location areas by.",
        required=True
    )


class LocationAreaName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationareaname.load(id)
