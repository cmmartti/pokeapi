# -*- coding: utf-8 -*-
import json
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection
from ..base import BaseConnection, BaseOrder, BaseName, BaseTranslationObject
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class PokemonForm(ObjectType):
    """
    Some Pokémon have the ability to take on different forms. At times, these differences are purely cosmetic and have no bearing on the difference in the Pokémon's stats from another; however, several Pokémon differ in stats (other than HP), type, and Ability depending on their form.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: PokemonFormName,
        description="The name of this Pokémon form listed in different languages."
    )
    form_name = String(
        description="The name of this form.",
        resolver=lambda root, info: root.form_name or None
    )
    form_names = TranslationList(
        lambda: PokemonFormFormName,
        description="The form specific form name of this Pokémon form, or empty if the form does not have a specific name."
    )
    order = Int(
        description="The order in which forms should be sorted within all forms. Multiple forms may have equal order, in which case they should fall back on sorting by name."
    )
    form_order = Int(
        description="The order in which forms should be sorted within a species' forms."
    )
    is_default = Boolean(
        description="True for exactly one form used as the default for each Pokémon."
    )
    is_battle_only = Boolean(
        description="Whether or not this form can only happen during battle."
    )
    is_mega = Boolean(
        description="Whether or not this form requires mega evolution."
    )
    pokemon_id = None
    pokemon = Field(
        lazy_import("pokemon_graphql.pokemon.types.Pokemon"),
        description="The Pokémon that can take on this form."
    )
    sprites = Field(
        lambda: PokemonFormSprites,
        description="A set of sprites used to depict this Pokémon form in the game."
    )
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group this Pokémon form was introduced in."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonform_names.load(key)

    def resolve_form_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokemonform_names.load(key)

    def resolve_pokemon(self, info, **kwargs):
        return info.context.loaders.pokemon.load(self.pokemon_id)

    def resolve_sprites(self, info):
        return info.context.loaders.pokemonform_sprites.load(self.id)

    def resolve_version_group(self, info, **kwargs):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonform.load(id)


class PokemonFormConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonForm


class PokemonFormOrdering(BaseOrder):
    sort = InputField(
        Enum('PokemonFormSort', [
            ("ORDER", "order"),
            ("FORM_ORDER", "form_order"),
            ("IS_DEFAULT", "is_default"),
            ("IS_BATTLE_ONLY", "is_battle_only"),
            ("IS_MEGA", "is_mega"),
            ("NAME", "name")
        ]),
        description="The field to sort by."
    )


class PokemonFormName(BaseTranslationObject):
    pokemon_name = None
    text = String(
        description="The full localized name for a Pokémon form in a specific language, e.g. \"Unown A\"."
    )

    def resolve_text(self, info):
        return self.pokemon_name or None

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonformname.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id)
        obj.pokemon_name = data.pokemon_name
        obj.language_id = data.language_id
        return obj


class PokemonFormFormName(BaseTranslationObject):
    name = String(
        name="text",
        description="The form-specific localized name for a Pokémon form in a specific language, e.g. \"A\" for Unown A."
    )

    def resolve_text(self, info):
        return self.name or None

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonformname.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, name=data.name)
        obj.language_id = data.language_id
        return obj


class PokemonFormSprites(ObjectType):
    sprites = None
    front_default = String(
        description="The default depiction of this Pokémon form from the front in battle.",
        resolver=lambda root, info: PokemonFormSprites.get_sprite(root, "front_default")
    )
    front_shiny = String(
        description="The shiny depiction of this Pokémon form from the front in battle.",
        resolver=lambda root, info: PokemonFormSprites.get_sprite(root, "front_shiny")
    )
    back_default = String(
        description="The default depiction of this Pokémon form from the back in battle.",
        resolver=lambda root, info: PokemonFormSprites.get_sprite(root, "back_default")
    )
    back_shiny = String(
        description="The shiny depiction of this Pokémon form from the back in battle.",
        resolver=lambda root, info: PokemonFormSprites.get_sprite(root, "back_shiny")
    )

    @staticmethod
    def get_sprite(self, sprite_name):
        sprites_data = json.loads(self.sprites)
        host = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/'

        if sprites_data[sprite_name]:
            return host + sprites_data[sprite_name].replace('/media/', '')
        return None

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonformsprites.load(id)
