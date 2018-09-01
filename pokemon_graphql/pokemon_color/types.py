# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class PokemonColor(ObjectType):
    """
    Colors used for sorting Pokémon in a Pokédex. The color listed in the Pokédex is usually the color most apparent or covering each Pokémon's body. No orange category exists; Pokémon that are primarily orange are listed as red or brown.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: PokemonColorName,
        description="The name of this Pokémon color listed in different languages."
    )
    pokemon_species = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesConnection"),
        description="A list of all Pokémon species that have this color.",
        where=Argument(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesWhere")
        ),
        order_by=Argument(List(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesOrdering")
        ))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemoncolor_names.load(key)

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.connection import PokemonSpeciesConnection

        q = models.PokemonSpecies.objects.filter(pokemon_color_id=self.id)
        return getConnection(q, PokemonSpeciesConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemoncolor.load(id)


class PokemonColorName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemoncolorname.load(id)
