# -*- coding: utf-8 -*-
from graphene import String, Boolean, Field, List, ObjectType, Enum, relay
from graphene import lazy_import

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder, BaseName
from ..relay_node import RelayNode
from ..field import TranslationList


class Generation(ObjectType):
    """
    A generation is a grouping of the Pokémon games that separates them based on the Pokémon they include. In each generation, a new set of Pokémon, Moves, Abilities and Types that did not exist in the previous generation are released.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: GenerationName,
        description="The name of this generation listed in different languages."
    )
    # abilities = relay.ConnectionField(
    #     lazy_import('pokemon_graphql.ability.types.Ability'),
    #     description="A list of abilities that were introduced in this generation.",
    #     where=Argument(lambda: Where), order_by=Argument(lambda: AbilityOrder)
    # )
    region_id = None
    main_region = Field(
        lazy_import('pokemon_graphql.region.types.Region'),
        description="The main region travelled in this generation."
    )
    # moves = relay.ConnectionField(
    #     lazy_import('pokemon_graphql.move.types.Move'),
    #     description="A list of moves that were introduced in this generation.",
    #     where=Argument(lambda: Where), order_by=Argument(lambda: MoveOrder)
    # )
    # pokemon_species = relay.ConnectionField(
    #     lazy_import('pokemon_graphql.pokemon_species.types.PokemonSpecies'),
    #     description="A list of Pokémon species that were introduced in this generation.",
    #     where=Argument(lambda: Where),
    #     order_by=Argument(lazy_import('pokemon_graphql.pokemon_species.types.PokemonSpeciesOrder'))
    # )
    # types = List(
    #     lazy_import('pokemon_graphql.type.types.Type'),
    #     description="A list of types that were introduced in this generation."
    # )
    version_groups = List(
        lazy_import('pokemon_graphql.version_group.types.VersionGroup'),
        description="A list of version groups that were introduced in this generation."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.generation_names.load(key)

    def resolve_abilities(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.abilities_by_generation.load(key)

    # def resolve_abilities(self, info, **kwargs):
    #     q = models.Ability.objects.all()
    #     return getConnection(q, AbilityConnection, **kwargs)

    def resolve_main_region(self, info, **kwargs):
        return info.context.loaders.region.load(self.region_id)

    # def resolve_moves(self, info, **kwargs):
    #     q = models.Move.objects.all()
    #     return getConnection(q, MoveConnection, **kwargs)

    # def resolve_pokemon_species(self, info, **kwargs):
    #     q = models.PokemonSpecies.objects.all()
    #     return getConnection(q, PokemonSpeciesConnection, **kwargs)

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


class GenerationOrderField(Enum):
    """Properties by which generation connections can be ordered."""

    NAME = "name"

    @property
    def description(self):
        if self == GenerationOrderField.NAME:
            return "Order generations by name."


class GenerationOrder(BaseOrder):
    """Ordering options for generation connections."""

    field = GenerationOrderField(
        description="The field to order generations by.",
        required=True
    )


class GenerationName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.generationname.load(id)
