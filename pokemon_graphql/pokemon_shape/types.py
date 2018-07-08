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


class PokemonShape(ObjectType):
    """
    Shapes used for sorting Pokémon in a Pokédex.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: PokemonShapeName,
        description="The name of this Pokémon shape listed in different languages."
    )
    pokemon_species = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_species.types.PokemonSpeciesConnection"),
        description="A list of the Pokémon species that have this shape.",
        where=Argument(Where),
        order_by=Argument(lazy_import(
            "pokemon_graphql.pokemon_species.types.PokemonSpeciesOrder"
        ))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonshape_names.load(key)

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.types import PokemonSpeciesConnection

        q = models.PokemonSpecies.objects.filter(pokemon_shape_id=self.id)
        return getConnection(q, PokemonSpeciesConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonshape.load(id)


class PokemonShapeName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonshapename.load(id)
