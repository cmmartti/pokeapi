# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class Region(ObjectType):
    """
    Regions that can be visited within the games. Regions make up sizable portions of regions, like cities or routes.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: RegionName,
        description="The name of this region listed in different languages."
    )
    main_generation = Field(
        lazy_import('pokemon_graphql.generation.types.Generation'),
        description="The generation this region was introduced in."
    )
    locations = relay.ConnectionField(
        lazy_import('pokemon_graphql.location.types.LocationConnection'),
        description="A list of locations that can be found in this region.",
        where=Argument(Where),
        order_by=Argument(List(
            lazy_import("pokemon_graphql.location.types.LocationOrdering")
        ))
    )
    pokedexes = List(
        lazy_import('pokemon_graphql.pokedex.types.Pokedex'),
        description="A lists of pokédexes that catalogue Pokémon in this region."
    )
    version_groups = List(
        lazy_import('pokemon_graphql.version_group.types.VersionGroup'),
        description="A list of version groups where this region can be visited."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.region_names.load(key)

    def resolve_main_generation(self, info, **kwargs):
        return info.context.loaders.generation_by_region.load(self.id)

    def resolve_locations(self, info, **kwargs):
        from ..location.types import LocationConnection

        q = models.Location.objects.filter(region_id=self.id)
        return getConnection(q, LocationConnection, **kwargs)

    def resolve_pokedexes(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokedexes_by_region.load(key)

    def resolve_version_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versiongroups_by_region.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.region.load(id)


class RegionConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Region


class RegionOrdering(BaseOrder):
    sort = InputField(
        Enum('RegionSort', [
            ("NAME", "name"),
            ("MAIN_GENERATION", "generation__id"),
        ]),
        description="The field to sort by."
    )


class RegionName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.regionname.load(id)
