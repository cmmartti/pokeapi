# -*- coding: utf-8 -*-
from graphene import relay, Argument, List

from pokemon_v2 import models
from ..base import BaseQuery
from .connection import ItemInterfaceConnection, ItemInterfaceOrdering, ItemInterfaceWhere, getItemConnection


class Query(BaseQuery):
    items = relay.ConnectionField(
        ItemInterfaceConnection,
        description="A list of items from the games.",
        where=Argument(ItemInterfaceWhere),
        order_by=Argument(List(ItemInterfaceOrdering))
    )

    def resolve_items(self, info, **kwargs):
        q = models.Item.objects.all()
        q = ItemInterfaceWhere.apply(q, **kwargs.get("where", {}))
        return getItemConnection(q, **kwargs)
