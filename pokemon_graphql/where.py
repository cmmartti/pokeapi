from graphene import String, InputObjectType, relay


class BaseWhere(InputObjectType):

    @staticmethod
    def get_id(global_id, expected_type, arg_name):
        actual_type, id = relay.Node.from_global_id(global_id)
        assert actual_type == expected_type, "Argument '%s' must be a global ID of type '%s', not '%s'." % (arg_name, expected_type, actual_type)
        return id

    @classmethod
    def apply(cls, query_set, **where):
        """Iteratively apply each where clause to the query_set."""
        for arg, value in where.iteritems():
            query_set = query_set.filter(**{arg: value})

        return query_set

class Where(BaseWhere):
    """Base filtering options for connections."""

    name = String(description="The exact full name of a resource.")
    name__icontains = String(
        name="name_contains",
        description="A partial case-insensitive match of the full name of a resource."
    )
