# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder, BaseName
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class Generation(ObjectType):
    """
    A generation is a grouping of the Pokémon games that separates them based on the Pokémon they include. In each generation, a new set of Pokémon, Moves, Abilities and Types that did not exist in the previous generation are released.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: GenerationName,
        description="The name of this generation listed in different languages."
    )
    abilities = relay.ConnectionField(
        lazy_import('pokemon_graphql.ability.types.AbilityConnection'),
        description="A list of abilities that were introduced in this generation.",
        where=Argument(lambda: Where),
        order_by=Argument(lazy_import("pokemon_graphql.ability.types.AbilityOrdering"))
    )
    region_id = None
    main_region = Field(
        lazy_import('pokemon_graphql.region.types.Region'),
        description="The main region travelled in this generation."
    )
    moves = relay.ConnectionField(
        lazy_import('pokemon_graphql.move.types.MoveConnection'),
        description="A list of moves that were introduced in this generation.",
        where=Argument(Where),
        order_by=Argument(List(lazy_import('pokemon_graphql.move.types.MoveOrdering')))
    )
    pokemon_species = relay.ConnectionField(
        lazy_import('pokemon_graphql.pokemon_species.connection.PokemonSpeciesConnection'),
        description="A list of Pokémon species that were introduced in this generation.",
        where=Argument(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesWhere")
        ),
        order_by=Argument(List(
            lazy_import('pokemon_graphql.pokemon_species.connection.PokemonSpeciesOrdering')
        ))
    )
    types = List(
        lazy_import('pokemon_graphql.type.types.Type'),
        description="A list of types that were introduced in this generation."
    )
    version_groups = List(
        lazy_import('pokemon_graphql.version_group.types.VersionGroup'),
        description="A list of version groups that were introduced in this generation."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.generation_names.load(key)

    def resolve_abilities(self, info, **kwargs):
        from ..ability.types import AbilityConnection

        q = models.Ability.objects.filter(generation_id=self.id)
        return getConnection(q, AbilityConnection, **kwargs)

    def resolve_main_region(self, info, **kwargs):
        return info.context.loaders.region.load(self.region_id)

    def resolve_moves(self, info, **kwargs):
        from ..move.types import MoveConnection

        q = models.Move.objects.filter(generation_id=self.id)
        return getConnection(q, MoveConnection, **kwargs)

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.connection import PokemonSpeciesConnection

        q = models.PokemonSpecies.objects.filter(generation_id=self.id)
        return getConnection(q, PokemonSpeciesConnection, **kwargs)

    def resolve_types(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.types_by_generation.load(key)

    def resolve_version_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versiongroups_by_generation.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.generation.load(id)


class GenerationConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Generation


class GenerationOrdering(BaseOrder):
    sort = InputField(
        Enum('GenerationSort', [
            ("MAIN_REGION", "region"),
            ("NAME", "name")
        ]),
        description="The field to sort by."
    )


class GenerationName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.generationname.load(id)
