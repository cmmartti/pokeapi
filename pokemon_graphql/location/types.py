# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from ..base import BaseConnection, BaseOrder, BaseName, BaseGenerationGameIndex
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class Location(ObjectType):
    """
    Locations that can be visited within the games. Locations make up sizable portions of regions, like cities or routes.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: LocationName,
        description="The name of this location listed in different languages."
    )
    areas = List(
        lazy_import('pokemon_graphql.location_area.types.LocationArea'),
        description="Areas that can be found within this location."
    )
    region_id = None
    region = Field(
        lazy_import('pokemon_graphql.region.types.Region'),
        description="The region this location can be found in."
    )
    game_indices = List(
        lambda: LocationGameIndex,
        description="A list of game indices relevent to this location by generation."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.location_names.load(key)

    def resolve_region(self, info, **kwargs):
        return info.context.loaders.region.load(self.region_id)

    def resolve_game_indices(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.location_gameindices.load(key)

    def resolve_areas(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.locationareas_by_location.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.location.load(id)


class LocationConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Location


class LocationOrdering(BaseOrder):
    sort = InputField(
        Enum('LocationSort', [
            ("REGION", "region__id"),
            ("NAME", "name"),
        ]),
        description="The field to sort by."
    )



class LocationName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationname.load(id)


class LocationGameIndex(BaseGenerationGameIndex):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationgameindex.load(id)
