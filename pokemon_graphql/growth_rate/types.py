# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class GrowthRate(ObjectType):
    """
    Growth rates are the speed with which Pokémon gain levels through experience. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Experience) for greater detail.
    """

    name = String(description="The name of this resource.")
    descriptions = TranslationList(
        lambda: GrowthRateDescription,
        description="The descriptions of this characteristic listed in different languages."
    )
    formula = String(
        description="The formula used to calculate the rate at which the Pokémon species gains level."
    )
    levels = List(
        lambda: GrowthRateExperienceLevel,
        description="A list of levels and the amount of experience needed to atain them based on this growth rate."
    )
    experience = Int(
        description="The experience needed to reach the given level at this growth rate.",
        level=Argument(Int, required=True)
    )
    pokemon_species = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesConnection"),
        description="A list of Pokémon species that gain levels at this growth rate.",
        where=Argument(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesWhere")
        ),
        order_by=Argument(List(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesOrdering")
        ))
    )

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.growthrate_descriptions.load(key)

    def resolve_levels(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.growthrate_experiences.load(key)

    def resolve_experience(self, info, level):
        key = LoaderKey(self.id, level=level)
        return info.context.loaders.growthrateexperience_by_level.load(key).then(
            lambda exp: exp.experience
        )

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.connection import PokemonSpeciesConnection

        q = models.PokemonSpecies.objects.filter(growth_rate_id=self.id)
        return getConnection(q, PokemonSpeciesConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.growthrate.load(id)


class GrowthRateDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.growthratedescription.load(id)


class GrowthRateExperienceLevel(ObjectType):
    level = Int(description="The level gained.")
    experience = Int(
        description="The amount of experience required to reach the referenced level."
    )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.experience.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        return cls(id=data.id, level=data.level, experience=data.experience)
