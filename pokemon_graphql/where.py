from graphene import String, Boolean, InputObjectType, relay


class BaseWhere(InputObjectType):

    @staticmethod
    def get_id(global_id, expected_type, arg_name):
        if global_id:
            actual_type, id = relay.Node.from_global_id(global_id)
            assert actual_type == expected_type, "Argument '%s' must be a global ID of type '%s', not '%s'." % (arg_name, expected_type, actual_type)
            return id
        return None

    @classmethod
    def apply(cls, query_set, **where):
        """Iteratively apply each where clause to query_set."""
        for arg, value in where.iteritems():
            query_set = query_set.filter(**{arg: value})

        return query_set.distinct()

class Where(BaseWhere):
    """Simple filtering options for connections."""

    name = String(description="The exact full name of a resource.")
    name__icontains = String(
        name="name_contains",
        description="A partial case-insensitive match of the full name of a resource."
    )


class TranslationSearch(InputObjectType):
    query = String(description="The search query.", required=True)
    case_sensitive = Boolean(
        default_value=False
    )
    # exact = Boolean(
    #     default_value=False,
    #     description="Return only exact, case-sensitive matches."
    # )
