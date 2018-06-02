# -*- coding: utf-8 -*-
from ..base import BaseQuery
from ..relay_node import RelayNode

class Query(BaseQuery):
    node = RelayNode.Field(description="Fetches an object given its ID.")
