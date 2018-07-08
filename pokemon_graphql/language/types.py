# -*- coding: utf-8 -*-
from graphene import String, Boolean, Field, List, ObjectType, Enum, relay
from graphene import lazy_import

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder
from ..relay_node import RelayNode
from ..field import TranslationList


class Language(ObjectType):
    """Languages for translations of resource information."""

    name = String(description="The name of this resource.")
    official = Boolean(
        description="Whether or not the games are published in this language."
    )
    iso639 = String(
        description="The two-letter code of the country where this language is spoken. Note that it is not unique."
    )
    iso3166 = String(
        description="The two-letter code of the language. Note that it is not unique."
    )
    names = TranslationList(
        lambda: LanguageName,
        description="The name of this language listed in different languages."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.language_names.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.language.load(id)


class LanguageConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Language


class LanguageOrderField(Enum):
    """Properties by which language connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == LanguageOrderField.NAME:
            return "Order languages by name."


class LanguageOrder(BaseOrder):
    """Ordering options for language connections."""
    field = LanguageOrderField(
        description="The field to order languages by.",
        required=True
    )


class LanguageName(ObjectType):
    name = String(
        name="text",
        description="The localized name for a resource in a specific language."
    )
    local_language_id = None
    local_language = Field(
        lambda: Language,
        description="The local language this language name is in."
    )

    def resolve_local_language(self, info):
        return info.context.loaders.language.load(self.local_language_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.languagename.load(id)
