# -*- coding: utf-8 -*-
from graphql_relay.connection.connectiontypes import Edge
from graphene import ID, Int, String, Boolean, Field, List
from graphene import ObjectType, Interface, Schema, relay

from .loader_key import LoaderKey
from .connections import getConnection
from pokemon_v2 import models


# Base field types
class RelayNode(relay.Node):
    class Meta:
        name = "Node"
        description = "An object with an ID."

    # For now, let us assume that the class name of the object (Django model)
    # returned by the resolver is also the name of the GraphQL object type
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance).__name__


class NameList(List):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("lang", String())
        super(NameList, self).__init__(type, *args, **kwargs)


# Base object classes
class Name(ObjectType):
    name = String(
        description="The localized name for a resource in a specific language."
    )
    language_id = None
    language = Field(
        lambda: Language,
        description="The language this name is in."
    )

    def resolve_language(self, info):
        return info.context.loaders.language.load(self.language_id)


#######################################
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
    names = NameList(
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


class LanguageConnection(relay.Connection):
    class Meta:
        node = Language


class LanguageName(ObjectType):
    name = String(
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
        return info.context.loaders.language_name.load(id)


#######################################
class Generation(ObjectType):
    """
    A generation is a grouping of the Pokémon games that separates them based on the Pokémon they include. In each generation, a new set of Pokémon, Moves, Abilities and Types that did not exist in the previous generation are released.
    """

    name = String(description="The name of this resource.")
    names = NameList(
        lambda: GenerationName,
        description="The name of this generation listed in different languages."
    )
    version_groups = List(
        lambda: VersionGroup,
        description="A list of version groups that were introduced in this generation."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.generation_names.load(key)

    def resolve_version_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versiongroups_by_generation.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.generation.load(id)


class GenerationConnection(relay.Connection):
    class Meta:
        node = Generation


class GenerationName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.generationname.load(id)


#######################################
class Version(ObjectType):
    """Versions of the games, e.g., Red, Blue or Yellow."""

    name = String(description="The name of this resource.")
    version_group_id = None
    names = NameList(
        lambda: VersionName,
        description="The name of this version listed in different languages."
    )
    version_group = Field(
        lambda: VersionGroup,
        description="The version group this version belongs to."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.version_names.load(key)

    def resolve_version_group(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.version.load(id)


class VersionConnection(relay.Connection):
    class Meta:
        node = Version


class VersionName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.versionname.load(id)


#######################################
class VersionGroup(ObjectType):
    """Version groups categorize highly similar versions of the games."""

    name = String(description="The name of this resource.")
    order = Int(description="Order for sorting. Almost by date of release, except similar versions are grouped together.")
    generation_id = None
    generation = Field(
        lambda: Generation,
        description="The generation this version was introduced in."
    )
    versions = List(
        lambda: Version,
        description="The versions this version group owns."
    )

    def resolve_generation(self, info):
        return info.context.loaders.generation.load(self.generation_id)

    def resolve_versions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versions_by_versiongroup.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.versiongroup.load(id)


class VersionGroupConnection(relay.Connection):
    class Meta:
        node = VersionGroup


#######################################
# Root Query

class Query(ObjectType):
    """The root query node."""

    node = RelayNode.Field(description="Fetches an object given its ID.")
    languages = relay.ConnectionField(
        LanguageConnection,
        description="A list of languages used for translations of resource information.",
        name=String()
    )
    generations = relay.ConnectionField(
        GenerationConnection,
        description="A list of generations (groupings of games based on the Pokémon they include).",
        name=String()
    )
    versions = relay.ConnectionField(
        VersionConnection,
        description="A list of versions of the games, e.g., Red, Blue or Yellow.",
        name=String()
    )
    version_groups = relay.ConnectionField(
        VersionGroupConnection,
        description="A list of version groups (highly similar versions of the games).",
        name=String()
    )

    def resolve_languages(self, info, **kwargs):
        q = models.Language.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return getConnection(q, LanguageConnection, **kwargs)

    def resolve_generations(self, info, **kwargs):
        q = models.Generation.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return getConnection(q, GenerationConnection, **kwargs)

    def resolve_versions(self, info, **kwargs):
        q = models.Version.objects.all()
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return getConnection(q, VersionConnection, **kwargs)

    def resolve_version_groups(self, info, **kwargs):
        q = models.VersionGroup.objects.all().order_by('order')
        if "name" in kwargs: q = q.filter(name=kwargs["name"])
        return getConnection(q, VersionGroupConnection, **kwargs)


schema = Schema(query=Query, auto_camelcase=True)
