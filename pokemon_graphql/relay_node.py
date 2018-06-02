from graphene.relay import Node

class RelayNode(Node):
    class Meta:
        name = "Node"
        description = "An object with an ID."

    # Let us assume that the class name of the object (Django model)
    # returned by the resolver is also the name of the GraphQL object type
    # When this assumption is not true, the `get_node` method on the type will
    # explicity return the correct type (look for the `fill` method).
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance).__name__
