from graphene import String, InputObjectType

class Where(InputObjectType):
    """Base filtering options for connections."""

    name = String(description="The full name of a resource.")
