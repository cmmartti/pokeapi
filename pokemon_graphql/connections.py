from graphql import GraphQLError
from graphql_relay.connection.connectiontypes import Edge
from graphene.relay.connection import PageInfo

from base64 import b64decode, b64encode
from cursor_pagination import CursorPaginator as CP, InvalidCursor


class CursorPaginator(CP):
    def decode_cursor(self, cursor):
        try:
            orderings = b64decode(cursor.encode('utf-8')).decode('utf-8')
            return orderings.split(self.delimiter)
        except (TypeError, ValueError):
            raise InvalidCursor(self.invalid_cursor_message)

    def encode_cursor(self, position):
        encoded = b64encode(self.delimiter.join(position).encode('utf-8')).decode('utf-8')
        return encoded


class Page(object):
    """
    An iterable object that holds page entries, as well as other page-related data.
    """

    def __init__(self, items, page_info, get_cursor, total_count=None):
        self.items = items
        self.page_info = page_info
        self.get_cursor = get_cursor
        self.total_count = total_count

    def __getitem__(self, key):
        return self.items.__getitem__(key)

    def __len__(self):
        return len(self.items)


def getPage(
    query_set,
    connection_name,
    first=None,
    last=None,
    after=None,
    before=None,
    order_by=[],
    **extra_kwargs_we_dont_care_about
):
    if first and last:
        raise GraphQLError("You must provide either `first` or `last` values (not both) to properly paginate `{0}`.".format(connection_name))
    if (first and before) or (last and after):
        raise GraphQLError("You must provide either `first`\`after` or `last`\`before` values to properly paginate `{0}`.".format(connection_name))
    if (first and first < 0)  or (last and last < 0):
        raise GraphQLError("You must provide a positive paging `limit` value to properly paginate `{0}`.".format(connection_name))
    if not first and not last:
        raise GraphQLError("You must provide a `first` or `last` value to properly paginate `{0}`.".format(connection_name))

    if order_by:
        # Probably not the best way...
        directions = [o["direction"] for o in order_by]
        if not len(set(directions)) == 1:
            raise GraphQLError("All `orderBy` entries must have the same `direction` value to properly sort `{0}`.".format(connection_name))

    # Total number of entries in the query set _before_ pagination.
    total_count = query_set.count()

    # Layer the orderBy, with `id` always at the bottom to ensure unique cursors.
    ordering = []
    for order in order_by:
        sort = order['sort']
        if order['direction'] == 'desc':
            sort = "-" + sort
        ordering.append(sort)

    if order_by and order_by[0].direction == "desc":
        ordering.append('-id')
    else:
        ordering.append('id')

    # Ordering is applied to the supplied Django query_set using CursorPaginator, below.

    # TODO: Catch incorrect cursor-related errors (the structure of a cursor changes
    # depending on the order_by argument, so passing in an invalid cursor will cause an exception).

    paginator = CursorPaginator(query_set, ordering=ordering)
    page = paginator.page(first=first, last=last, after=after, before=before)

    # If there are no results, there can be no cursors.
    if page:
        start_cursor = paginator.cursor(page[0])
        end_cursor = paginator.cursor(page[-1])
    else:
        start_cursor = None
        end_cursor = None

    return Page(
        items=page,
        page_info=PageInfo(
            start_cursor=start_cursor,
            end_cursor=end_cursor,
            has_previous_page=page.has_previous,
            has_next_page=page.has_next
        ),
        total_count=total_count,
        get_cursor=paginator.cursor
    )


def getConnection(query_set, connection_type, get_node_fn=None, **kwargs):
    page = getPage(query_set, connection_type.__name__, **kwargs)
    edges = []
    for item in page.items:
        if get_node_fn:
            node = get_node_fn(item)
        else:
            node = item
        edges.append(Edge(node=node, cursor=page.get_cursor(item)))

    return connection_type(
        total_count=page.total_count,
        edges=edges,
        page_info=page.page_info
    )
