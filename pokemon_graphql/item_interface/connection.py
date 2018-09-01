from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..util import merge_dicts
from ..connections import getPage
from ..base import BaseConnection, BaseOrder
from .types import ItemInterface
from ..item.types import Item
from ..berry.types import Berry
from ..where import BaseWhere


class ItemInterfaceConnection(BaseConnection, relay.Connection):
    class Meta:
        node = ItemInterface


class ItemInterfaceOrdering(BaseOrder):
    sort = InputField(
        Enum('ItemInterfaceSort', [
            ("CATEGORY", "item_category__id"),
            ("COST", "cost"),
            ("FLING_POWER", "fling_power"),
            ("FLING_EFFECT", "item_fling_effect__id"),
            ("NAME", "name")
        ]),
        description="The field to sort by."
    )


class ItemInterfaceWhere(BaseWhere):
    item_category_id = ID(
        name="categoryID",
        description="The global ID of an item's category."
    )

    @classmethod
    def apply(cls, query_set, **where):

        item_category_id = where.pop("item_category_id", None)
        if item_category_id:
            id = cls.get_id(item_category_id, "ItemCategory", "categoryID")
            query_set = query_set.filter(item_category_id=id)

        return super(ItemInterfaceWhere, cls).apply(query_set, **where)



def getItemConnection(q, **kwargs):
    q = q.prefetch_related("berry")
    q = ItemInterfaceWhere.apply(q, **kwargs.get("where", {}))
    page = getPage(q, ItemInterfaceConnection.__name__, **kwargs)

    edges = []
    for item in page:
        edges.append(
            ItemInterfaceConnection.Edge(
                node=get_item_node(item),
                cursor=page.get_cursor(item)
            )
        )

    return ItemInterfaceConnection(
        edges=edges,
        page_info=page.page_info,
        total_count=page.total_count,
    )


def get_item_node(item):
    """
    Given a Django Item query set object, return the appropriate ItemInterface node.
    """

    attr = {
        "name": item.name,
        "cost": item.cost,
        "fling_power": item.fling_power,
    }

    berries = list(item.berry.all())
    if len(berries) == 1:
        berry = berries[0]
        berry_attr = {
            "id": item.id,
            "growth_time": berry.growth_time,
            "max_harvest": berry.max_harvest,
            "natural_gift_power": berry.natural_gift_power,
            "size": berry.size,
            "smoothness": berry.smoothness,
            "soil_dryness": berry.soil_dryness,
        }
        attr = merge_dicts(attr, berry_attr)
        node = Berry(**attr)

        node.berry_id = berry.id
        node.berry_firmness_id = berry.berry_firmness_id
        node.natural_gift_type_id = berry.natural_gift_type_id
    else:
        node = Item(id=item.id, **attr)

    node.item_id = item.id
    node.item_fling_effect_id = item.item_fling_effect_id
    node.item_category_id = item.item_category_id

    return node
