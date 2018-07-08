
from graphql import GraphQLError
from cursor_pagination import CursorPaginator
from graphql_relay.connection.connectiontypes import Edge
from graphene.relay.connection import PageInfo


class Page(object):
    """
    An iterable object that holds page entries, as well as other page-related data.
    """

    def __init__(self, data, page_info, get_cursor, total_count=None):
        self._entries = data
        self.page_info = page_info
        self.get_cursor = get_cursor
        self.total_count = total_count

    def __getitem__(self, item):
        if item >= len(self._entries):
            raise IndexError("Page index out of range")
        return self._entries[item]

    def __len__(self):
        return len(self._entries)


def getPage(
    query_set,
    connection_name,
    first=None,
    last=None,
    after=None,
    before=None,
    order_by=None,
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

    # Layer the ordering, with `id` always at the bottom to ensure unique cursors
    reverse = False
    ordering = []
    if order_by:
        field = order_by['field']
        reverse = (order_by['direction'] == 'desc')
        ordering.append(field)
    ordering.append('id')

    if reverse:
        ordering = [("-" + o) for o in ordering]

    # Total number of entries in the query set before paging
    total_count = query_set.count()

    # TODO: Catch incorrect cursor-related errors (the structure of a cursor changes
    # depending on the order_by argument, so passing in an invalid cursor will fail).

    paginator = CursorPaginator(query_set, ordering=ordering)
    page = paginator.page(first=first, last=last, after=after, before=before)

    # If there are no results, there can be no cursor
    if page:
        start_cursor = paginator.cursor(page[0])
        end_cursor = paginator.cursor(page[-1])
    else:
        start_cursor = None
        end_cursor = None

    return Page(
        data=page,
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
    for item in page:
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
