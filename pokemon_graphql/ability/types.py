# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseEffect, BaseVerboseEffect, BaseFlavorText
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class Ability(ObjectType):
    """
    Abilities provide passive effects for Pokémon in battle or in the overworld. Pokémon have multiple possible abilities but can have only one ability at a time. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Ability) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: AbilityName,
        description="The name of this ability listed in different languages."
    )
    is_main_series = Boolean(
        description="Whether or not this ability originated in the main series of the video games."
    )
    generation_id = None
    generation = Field(
        lazy_import("pokemon_graphql.generation.types.Generation"),
        description="The generation this ability originated in."
    )
    effect_entries = TranslationList(
        lambda: AbilityEffect,
        description="The effect of this ability listed in different languages."
    )
    effect_changes = List(
        lambda: AbilityEffectChange,
        description="The list of previous effects this ability has had across version groups."
    )
    flavor_text_entries = TranslationList(
        lambda: AbilityFlavorText,
        description="The flavor text of this ability listed in different languages."
    )
    pokemon = relay.ConnectionField(
        lambda: AbilityPokemonConnection,
        description="A list of Pokémon that could potentially have this ability.",
        where=Argument(lambda: AbilityPokemonWhere),
        order_by=List(lambda: AbilityPokemonOrdering)
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.ability_names.load(key)

    def resolve_generation(self, info):
        return info.context.loaders.generation.load(self.generation_id)

    def resolve_effect_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.ability_effectentries.load(key)

    def resolve_effect_changes(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.ability_changes.load(key)

    def resolve_flavor_text_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.ability_flavortextentries.load(key)

    def resolve_pokemon(self, info, **kwargs):
        q = models.PokemonAbility.objects.filter(ability_id=self.id)
        q = q.select_related('pokemon')

        page = getPage(q, AbilityPokemonConnection.__name__, **kwargs)
        edges = []
        for entry in page:
            edges.append(AbilityPokemonConnection.Edge(
                node=entry.pokemon,
                is_hidden=entry.is_hidden,
                slot=entry.slot,
                cursor=page.get_cursor(entry)
            ))
        return AbilityPokemonConnection(
            edges=edges,
            page_info=page.page_info,
            total_count=page.total_count,
        )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.ability.load(id)


class AbilityConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Ability


class AbilityOrdering(BaseOrder):
    sort = InputField(
        Enum('AbilitySort', [
            ("IS_MAIN_SERIES", "is_main_series"),
            ("GENERATION", "generation"),
            ("NAME", "name")
        ]),
        description="The field to sort by."
    )


class AbilityName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.abilityname.load(id)


class AbilityEffect(BaseVerboseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.abilityeffect.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id)
        obj.effect = data.effect
        obj.short_effect = data.short_effect
        obj.language_id = data.language_id
        return obj


class AbilityEffectChange(ObjectType):
    effect_entries = TranslationList(
        lambda: AbilityChangeEffectText,
        description="The previous effect of this ability listed in different languages."
    )
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group in which the previous effect of this ability originated."
    )

    def resolve_effect_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.abilitychange_effectentries.load(key)

    def resolve_version_group(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.abilitychange.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id)
        obj.version_group_id = data.version_group_id
        return obj


class AbilityChangeEffectText(BaseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.abilitychangeeffect.load(id)


class AbilityFlavorText(BaseFlavorText):
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group that uses this flavor text."
    )

    def resolve_version_group(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.abilityflavortext.load(id)


from ..pokemon.types import Pokemon
class AbilityPokemonConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Pokemon

    class Edge:
        is_hidden = Boolean(
            description="Whether or not this a hidden ability for the referenced Pokémon."
        )
        slot = Int(
            description="Pokémon have 3 ability 'slots' which hold references to possible abilities they could have. This is the slot of this ability for the referenced pokemon."
        )


class AbilityPokemonOrderField(Enum):
    """Properties by which ability Pokémon connections can be ordered."""
    NAME = "name"
    SLOT = "slot"

    @property
    def description(self):
        if self == AbilityPokemonOrderField.NAME:
            return "Order by name."
        elif self == AbilityPokemonOrderField.SLOT:
            return "Order by ability slot."


class AbilityPokemonOrdering(BaseOrder):
    sort = InputField(
        Enum('AbilityPokemonSort', [
            ("IS_HIDDEN", "is_hidden"),
            ("SLOT", "slot"),
        ]),
        description="The field to sort by."
    )


class AbilityPokemonWhere(Where):
    """Filtering options for Ability Pokémon connections."""

    is_hidden = Boolean(
        description="Filter by whether this Pokémon's ability is hidden."
    )
