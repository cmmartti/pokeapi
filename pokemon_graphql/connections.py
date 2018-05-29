
from graphql import GraphQLError
from cursor_pagination import CursorPaginator
from graphql_relay.connection.connectiontypes import Edge
from graphene.relay.connection import PageInfo


class Page(object):
    def __init__(self, data, page_info, get_cursor):
        self.data = data
        self.page_info = page_info
        self.get_cursor = get_cursor


def getPage(
    query_set,
    connection_name,
    first=None,
    last=None,
    after=None,
    before=None,
    order_by=None,
    where=None
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

    # Filter by the arguments in `where`
    if where:
        for arg, value in where.iteritems():
            query_set = query_set.filter(**{arg: value})


    # TODO: Catch incorrect cursor-related errors (cursors change depending on the order_by argument)

    paginator = CursorPaginator(query_set, ordering=ordering)
    page = paginator.page(first=first, last=last, after=after, before=before)

    return Page(
        data=page,
        page_info=PageInfo(
            start_cursor=paginator.cursor(page[0]),
            end_cursor=paginator.cursor(page[-1]),
            has_previous_page=page.has_previous,
            has_next_page=page.has_next
        ),
        get_cursor=paginator.cursor
    )


def getConnection(query_set, connection_type, **kwargs):
    page = getPage(query_set, connection_type.__name__, **kwargs)
    edges = []
    for item in page.data:
        edges.append(Edge(node=item, cursor=page.get_cursor(item)))

    return connection_type(edges=edges, page_info=page.page_info)
