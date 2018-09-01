# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getPage
from ..base import BaseConnection, BaseOrder, BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where
from ..pokemon_species.types import PokemonSpecies


class PalParkArea(ObjectType):
    """
    Areas used for grouping Pokémon encounters in Pal Park. They're like habitats that are specific to Pal Park.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: PalParkAreaName,
        description="The name of this pal park area listed in different languages."
    )
    pokemon_encounters = relay.ConnectionField(
        lambda: PalParkEncounterSpeciesConnection,
        description="A list of Pokémon encountered in this pal park area along with details.",
        order_by=Argument(List(lambda: PalParkEncounterSpeciesOrdering)),
        where=Argument(Where)
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.palparkarea_names.load(key)

    def resolve_pokemon_encounters(self, info, **kwargs):
        q = models.PalPark.objects.filter(pal_park_area_id=self.id)
        q = Where.apply(q, **kwargs.get("where", {}))
        page = getPage(q, PalParkEncounterSpeciesConnection.__name__, **kwargs)

        return PalParkEncounterSpeciesConnection(
            edges=[
                PalParkEncounterSpeciesConnection.Edge(
                    base_score=entry.base_score,
                    node=entry.pokemon_species,
                    rate=entry.rate
                ) for entry in page
            ],
            page_info=page.page_info,
            total_count=page.total_count
        )

        return getConnection(q, PalParkEncounterSpeciesConnection, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.palparkarea.load(id)


class PalParkAreaName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.palparkareaname.load(id)


class PalParkEncounterSpeciesConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonSpecies

    class Edge:
        base_score = Int(
            description="The base score given to the player when this Pokémon is caught during a pal park run."
        )
        rate = Int(
            description="The base rate for encountering this Pokémon in this pal park area."
        )


class PalParkEncounterSpeciesOrdering(BaseOrder):
    sort = InputField(
        Enum('PalParkEncounterSpeciesSort', [
            ("BASE_SCORE", "base_score"),
            ("RATE", "rate"),
        ]),
        description="The field to sort by."
    )
