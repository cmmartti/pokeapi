# -*- coding: utf-8 -*-
from graphene import *


class BaseQuery(ObjectType):
    pass


class BaseMutation(ObjectType):
    pass


class BaseSubscription(ObjectType):
    pass


class BaseConnection(object):
    total_count = Int(
        description='A count of the total number of objects in this connection, ignoring pagination. This allows a client to fetch the first five objects by passing "5" as the argument to "first", then fetch the total count so it could display "5 of 83", for example.'
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


class BaseTranslationObject(ObjectType):
    language_id = None
    language = Field(
        lazy_import("pokemon_graphql.language.types.Language"),
        description="The language this translation is in.",
        resolver=lambda root, info: info.context.loaders.language.load(root.language_id)
    )
    text = String(
        description="The localized text for a resource in a specific language."
    )


class BaseName(BaseTranslationObject):
    name = String(
        name="text",
        description="The localized name for a resource in a specific language."
    )


class BaseDescription(BaseTranslationObject):
    description = String(
        name="text",
        description="The localized description for a resource in a specific language."
    )


class BaseEffect(BaseTranslationObject):
    effect = String(
        name="text",
        description="The localized effect text for a resource in a specific language."
    )


class BaseVerboseEffect(BaseEffect):
    short_effect = String(
        name="shortText",
        description="The localized effect text in brief."
    )


class BaseFlavorText(BaseTranslationObject):
    flavor_text = String(
        name="text",
        description="The localized flavor text for a resource in a specific language."
    )


class BaseGameIndex(ObjectType):
    game_index = Int(description='The internal id of a resource within game data.')


class BaseGenerationGameIndex(BaseGameIndex):
    generation_id = None
    generation = Field(
        lazy_import('pokemon_graphql.generation.types.Generation'),
        description='The generation relevent to this game index.'
    )

    def resolve_generation(self, info):
        return info.context.loaders.generation.load(self.generation_id)


class BaseVersionGameIndex(BaseGameIndex):
    version_id = None
    version = Field(
        lazy_import('pokemon_graphql.version.types.Version'),
        description='The version relevent to this game index.'
    )

    def resolve_version(self, info):
        return info.context.loaders.version.load(self.version_id)
