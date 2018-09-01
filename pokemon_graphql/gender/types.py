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


class Gender(ObjectType):
    """
    Genders were introduced in Generation II for the purposes of breeding Pokémon but can also result in visual differences or even different evolutionary lines. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Gender) for greater detail.
    """

    name = String(description="The name of this resource.")
    pokemon_species = relay.ConnectionField(
        lambda: GenderPokemonSpeciesConnection,
        description="A list of Pokémon species that can be this gender and how likely it is that they will be, as well as if it's required for evolution.",
        where=Argument(lambda: GenderPokemonSpeciesWhere),
        order_by=Argument(List(lambda: GenderPokemonSpeciesOrdering))
    )

    def resolve_pokemon_species(self, info, **kwargs):
        if self.name == "male":
            q = models.PokemonSpecies.objects.filter(gender_rate__gt=0)
        elif self.name == "female":
            q = models.PokemonSpecies.objects.filter(gender_rate__range=[0, 7])
        elif self.name == "genderless":
            q = models.PokemonSpecies.objects.filter(gender_rate=-1)

        # TODO: This fails for some reason
        # q = q.select_related("pokemonevolution")

        # if "where" in kwargs and "required_for_evolution" in kwargs["where"]:
        #     req = kwargs["where"]["required_for_evolution"]
        #     if req:
        #         q = q.filter(pokemonevolution__gender_id=self.id)
        #     elif not req:
        #         q = q.exclude(pokemonevolution__gender_id=self.id)

        #     del kwargs["where"]["required_for_evolution"]

        page = getPage(q, GenderPokemonSpeciesConnection.__name__, **kwargs)
        edges = []
        for entry in page:
            edges.append(GenderPokemonSpeciesConnection.Edge(
                node=entry,
                rate=entry.gender_rate,
                # required_for_evolution=entry.pokemonevolution.gender_id == self.id,
                cursor=page.get_cursor(entry),
            ))
        return GenderPokemonSpeciesConnection(
            edges=edges,
            page_info=page.page_info,
            total_count=page.total_count,
        )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.gender.load(id)


from ..pokemon_species.types import PokemonSpecies
class GenderPokemonSpeciesConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonSpecies

    class Edge:
        rate = Int(
            description="The chance of this Pokémon being female, in eighths; or -1 for genderless."
        )
        # required_for_evolution = Boolean(
        #     description="Whether this Pokémon species required this gender in order for a Pokémon to evolve into them."
        # )


class GenderPokemonSpeciesOrdering(BaseOrder):
    sort = InputField(
        Enum('GenderPokemonSpeciesSort', [
            ("RATE", "gender_rate"),
            # ("REQUIRED_FOR_EVOLUTION", "required_for_evolution"),
        ]),
        description="The field to sort by."
    )


class GenderPokemonSpeciesWhere(Where):
    """Filtering options for gender Pokémon species connections."""
    pass
    # required_for_evolution = Boolean(
    #     description="Filter by whether this gender is required for this Pokémon to evolve."
    # )
