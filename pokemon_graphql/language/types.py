# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from ..loader_key import LoaderKey
from ..base import BaseConnection, BaseOrder
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import BaseWhere


class Language(ObjectType):
    """Languages for translations of resource information."""

    name = String(description="The name of this resource.")
    official = Boolean(
        name="isOfficial",
        description="Whether or not the games are published in this language."
    )
    iso639 = String(
        name="countryCode",
        description="The ISO 639 two-letter code of the country where this language is spoken. Note that it is not unique."
    )
    iso3166 = String(
        name="languageCode",
        description="The ISO3166 two-letter code of the language. Note that it is not unique."
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


class LanguageOrdering(BaseOrder):
    sort = InputField(
        Enum('LanguageSort', [
            ("IS_OFFICIAL", "official"),
            ("COUNTRY_CODE", "iso639"),
            ("LANGUAGE_CODE", "iso3166"),
            ("NAME", "name")
        ]),
        description="The field to sort by."
    )


class LanguageWhere(BaseWhere):
    official = Boolean(name="isOfficial")


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
