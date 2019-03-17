import graphene as g
from pokemon_v2 import models
from graphql_api.utils import get_connection
from . import types
from . import connection as conn
from ..base import BaseQuery


class Query(BaseQuery):
    region = g.Field(types.Region, id_name=g.ID(required=True))
    regions = g.relay.ConnectionField(
        conn.RegionConnection,
        description="A list of regions (organized areas) of the Pokémon world.",
        order_by=g.List(conn.RegionSort),
        where=g.Argument(conn.RegionWhere)
    )

    def resolve_region(self, info, id_name):
        return info.context.loaders.n_region.load(id_name)

    def resolve_regions(self, info, where=None, order_by=None, **kwargs):
        where = where or {}
        q = models.Region.objects.all()
        q = conn.RegionWhere.apply(q, **where)
        q, order_by = conn.RegionSort.apply(q, order_by)
        return get_connection(q, order_by, conn.RegionConnection, **kwargs)
