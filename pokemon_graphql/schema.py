
from graphene import Schema

from .auto import schema_operations_builder
from .item.types import Item
from .berry.types import Berry


ALL_QUERIES = schema_operations_builder(
    operationName='Query',
    operationModule='query',
    operationBase='BaseQuery',
    clsName='Query'
)

schema = Schema(query=ALL_QUERIES, types=[Item, Berry])
