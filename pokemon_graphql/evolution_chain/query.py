# -*- coding: utf-8 -*-
from graphene import List, Argument, String, relay
from graphene.relay import Node

from pokemon_v2 import models
from ..base import BaseQuery
from ..connections import getConnection
from .types import EvolutionChainConnection, EvolutionChainOrder, EvolutionChainWhere


class Query(BaseQuery):
    evolution_chains = relay.ConnectionField(
        EvolutionChainConnection,
        description="A list of evolution chains (family trees) for Pokémon.",
        order_by=Argument(EvolutionChainOrder),
        where=Argument(EvolutionChainWhere)
    )

    def resolve_evolution_chains(self, info, **kwargs):
        q = models.EvolutionChain.objects.all()
        q = EvolutionChainWhere.apply(q, **kwargs.get("where", {}))
        return getConnection(q, EvolutionChainConnection, **kwargs)
