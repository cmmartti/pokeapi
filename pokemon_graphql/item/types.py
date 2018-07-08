# -*- coding: utf-8 -*-
import json
from graphene import *

from ..interfaces import RelayNode
from ..item_interface.types import ItemInterface


class Item(ObjectType):
    """
    An item is an object in the games which the player can pick up, keep in their bag, and use in some manner. They have various uses, including healing, powering up, helping catch Pokémon, or to access a new area.
    """

    class Meta:
        interfaces = (ItemInterface, RelayNode)

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.item.load(id)
