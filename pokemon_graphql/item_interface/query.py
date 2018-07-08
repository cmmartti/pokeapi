# -*- coding: utf-8 -*-
from graphene import relay, Argument

from pokemon_v2 import models
from ..base import BaseQuery
from .connection import ItemInterfaceConnection, ItemInterfaceOrder, ItemInterfaceWhere, getItemConnection


class Query(BaseQuery):
    items = relay.ConnectionField(
        ItemInterfaceConnection,
        description="A list of items from the games.",
        order_by=Argument(ItemInterfaceOrder),
        where=Argument(ItemInterfaceWhere)
    )

    def resolve_items(self, info, **kwargs):
        q = models.Item.objects.all()
        q = ItemInterfaceWhere.apply(q, **kwargs.get("where", {}))
        return getItemConnection(q, **kwargs)
