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


class EggGroup(ObjectType):
    """
    Egg Groups are categories which determine which Pokémon are able to interbreed. Pokémon may belong to either one or two Egg Groups. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Egg_Group) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: EggGroupName,
        description="The names of this egg group listed in different languages."
    )
    pokemon_species = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_species.types.PokemonSpeciesConnection"),
        description="A list of all Pokémon species that are members of this egg group.",
        where=Argument(Where),
        order_by=Argument(lazy_import(
            "pokemon_graphql.pokemon_species.types.PokemonSpeciesOrder"
        ))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.egggroup_names.load(key)

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.types import PokemonSpeciesConnection

        q = models.PokemonSpecies.objects.filter(pokemonegggroup__egg_group_id=self.id)
        return getConnection(q, PokemonSpeciesConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.egggroup.load(id)


class EggGroupConnection(BaseConnection, relay.Connection):
    class Meta:
        node = EggGroup


class EggGroupOrderField(Enum):
    """Properties by which egg group connections can be ordered."""

    NAME = "name"

    @property
    def description(self):
        if self == EggGroupOrderField.NAME:
            return "Order by name."


class EggGroupOrder(BaseOrder):
    """Ordering options for egg group connections."""

    field = EggGroupOrderField(
        description="The field to order edges by.",
        required=True
    )


class EggGroupName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.egggroupname.load(id)
