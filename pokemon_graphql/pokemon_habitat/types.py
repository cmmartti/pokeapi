# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class PokemonHabitat(ObjectType):
    """
    Habitats are generally different terrain Pokémon can be found in but can also be areas designated for rare or legendary Pokémon.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: PokemonHabitatName,
        description="The name of this Pokémon habitat listed in different languages."
    )
    pokemon_species = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesConnection"),
        description="A list of the Pokémon species that can be found in this habitat",
        where=Argument(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesWhere")
        ),
        order_by=Argument(List(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesOrdering")
        ))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonhabitat_names.load(key)

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.connection import PokemonSpeciesConnection

        q = models.PokemonSpecies.objects.filter(pokemon_habitat_id=self.id)
        return getConnection(q, PokemonSpeciesConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonhabitat.load(id)


class PokemonHabitatName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonhabitatname.load(id)
