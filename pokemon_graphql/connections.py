
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
    ordering=(),
    **kwargs
):
    if not ordering: ordering = ()

    if first and last:
        raise GraphQLError("You must provide either `first` or `last` values (not both) to properly paginate `%s`." % connection_name)
    if (first and before) or (last and after):
        raise GraphQLError("You must provide either `first`\`after` or `last`\`before` values to properly paginate `%s`." % connection_name)
    if (first and first < 0)  or (last and last < 0):
        raise GraphQLError("You must provide a positive paging `limit` value to properly paginate `%s`." % connection_name)
    if not first and not last:
        raise GraphQLError("You must provide a `first` or `last` value to properly paginate `%s`." % connection_name)

    args = {}
    if first: args["first"] = first
    if last: args["last"] = last
    if after: args["after"] = after
    if before: args["before"] = before

    paginator = CursorPaginator(query_set, ordering=ordering + ("id", ))
    page = paginator.page(**args)

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
