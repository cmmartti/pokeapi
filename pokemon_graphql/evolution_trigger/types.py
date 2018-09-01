# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay
from django.db.models import Prefetch

from pokemon_v2 import models
from ..connections import getPage
from ..base import BaseName
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class EvolutionTrigger(ObjectType):
    """
    Evolution triggers are the events and conditions that cause a Pokémon to evolve. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Methods_of_evolution) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: EvolutionTriggerName,
        description="The name of this evolution trigger listed in different languages."
    )
    pokemon_species = relay.ConnectionField(
        lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesConnection"),
        description="A list of pokemon species that result from this evolution trigger.",
        where=Argument(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesWhere")
        ),
        order_by=Argument(List(
            lazy_import("pokemon_graphql.pokemon_species.connection.PokemonSpeciesOrdering")
        ))
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.evolutiontrigger_names.load(key)

    def resolve_pokemon_species(self, info, **kwargs):
        from ..pokemon_species.connection import PokemonSpeciesConnection

        q = models.PokemonEvolution.objects.filter(evolution_trigger_id=self.id)
        q = q.select_related("evolved_species")

        page = getPage(q, PokemonSpeciesConnection.__name__, **kwargs)
        edges = []
        for entry in page:
            edges.append(PokemonSpeciesConnection.Edge(
                node=entry.evolved_species,
                cursor=page.get_cursor(entry),
            ))
        return PokemonSpeciesConnection(
            edges=edges,
            page_info=page.page_info,
            total_count=page.total_count,
        )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.evolutiontrigger.load(id)


class EvolutionTriggerName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.evolutiontriggername.load(id)
