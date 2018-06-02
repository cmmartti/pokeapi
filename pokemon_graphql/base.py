from graphene import ObjectType, InputObjectType, String, Field, Enum, Int
from graphene import lazy_import


class BaseQuery(ObjectType):
    pass


class BaseMutation(ObjectType):
    pass


class BaseSubscription(ObjectType):
    pass


class BaseConnection(object):
    totalCount = Int(
        description="Identifies the total count of items in the connection."
    )


class OrderDirection(Enum):
    ASC = "asc"
    DESC = "desc"

    @property
    def description(self):
        if self == OrderDirection.ASC:
            return "Specifies an ascending order for a given orderBy argument."
        if self == OrderDirection.DESC:
            return "Specifies a descending order for a given orderBy argument."


class BaseOrder(InputObjectType):
    direction = OrderDirection(description="The ordering direction.", required=True)


class BaseName(ObjectType):
    name = String(
        description="The localized name for a resource in a specific language."
    )
    language_id = None
    language = Field(
        lazy_import("pokemon_graphql.language.types.Language"),
        description="The language this name is in.",
        resolver=lambda root, info: info.context.loaders.language.load(self.language_id)
    )


class BaseGenerationGameIndex(ObjectType):
    game_index = Int(description='The internal id of a resource within game data.')
    generation = Field(
        lazy_import('pokemon_graphql.generation.types.Generation'),
        description='The generation relevent to this game index.'
    )
