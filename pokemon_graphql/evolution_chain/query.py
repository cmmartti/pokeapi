# -*- coding: utf-8 -*-
from graphene import relay, Argument, List
from graphene.relay import Node

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import EvolutionChainConnection, EvolutionChainOrdering, EvolutionChainWhere


class Query(BaseQuery):
    evolution_chains = relay.ConnectionField(
        EvolutionChainConnection,
        description="A list of evolution chains (family trees) for Pokémon.",
        where=Argument(EvolutionChainWhere),
        order_by=Argument(List(EvolutionChainOrdering))
    )

    def resolve_evolution_chains(self, info, **kwargs):
        q = models.EvolutionChain.objects.all()
        q = EvolutionChainWhere.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EvolutionChainConnection, **kwargs)
