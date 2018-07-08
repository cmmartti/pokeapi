# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..interfaces import RelayNode, SimpleEdge
from ..loader_key import LoaderKey
from ..base import BaseConnection
from ..move.types import Move


class PokemonAbilityEdge(ObjectType):
    # TODO: what are "hidden" abilities? Description should say what that means.
    is_hidden = Boolean(description="Whether or not this is a hidden ability.")
    slot = Int(description="The slot this ability occupies in this Pokémon species.")
    ability_id = None
    node = Field(
        lazy_import("pokemon_graphql.ability.types.Ability"),
        description="The ability the Pokémon may have."
    )

    def resolve_node(self, info):
        return info.context.loaders.ability.load(self.ability_id)

    class Meta:
        interfaces = (SimpleEdge, )

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id)
        obj.is_hidden = data.is_hidden
        obj.slot = data.slot
        obj.ability_id = data.ability_id


class PokemonHeldItem(ObjectType):
    item_id = None
    pokemon_id = None
    node = Field(
        lazy_import("pokemon_graphql.item_interface.types.ItemInterface"),
        description="The item the referenced Pokémon holds."
    )
    versions = List(
        lambda: PokemonHeldItemVersion,
        description="The details of the different versions in which the item is held."
    )

    def resolve_node(self, info):
        return info.context.loaders.item.load(self.item_id).then(PokemonHeldItem.get_item_node)

    @staticmethod
    def get_item_node(item):
        from ..item_interface.connection import get_item_node
        return get_item_node(item)

    def resolve_versions(self, info):
        pokemon_items = models.PokemonItem.objects.filter(
            item_id=self.item_id, pokemon_id=self.pokemon_id
        )

        # Group pokemon_items by version
        versions = {}
        for pi in pokemon_items:
            if pi.version_id not in versions:
                pkmn_held_itm_ver = PokemonHeldItemVersion()
                pkmn_held_itm_ver.rarity = pi.rarity
                pkmn_held_itm_ver.version_id = pi.version_id
                versions[pi.version_id] = pkmn_held_itm_ver
        return versions.values()

    # class Meta:
    #     interfaces = (SimpleEdge, )


class PokemonHeldItemVersion(ObjectType):
    rarity = Int(description="How often the item is held.")
    version_id = None
    node = Field(
        lazy_import("pokemon_graphql.version.types.Version"),
        description="The version in which the item is held."
    )

    def resolve_node(self, info):
        return info.context.loaders.version.load(self.version_id)

    class Meta:
        interfaces = (SimpleEdge, )


class PokemonMoveConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Move

    class Edge:
        move_id = None
        pokemon_id = None
        version_groups = List(
            lambda: PokemonMoveVersion,
            description="The details of the version group in which the Pokémon can learn the move."
        )

        def resolve_version_groups(self, info):
            key = LoaderKey(0, move_id=self.move_id, pokemon_id=self.pokemon_id)
            return info.context.loaders.pokemonmove_by_move_and_pokemon.load(key).then(
                lambda data: PokemonMoveConnection.Edge.get_version_groups(self, data)
            )

        @staticmethod
        def get_version_groups(root, pokemon_moves):

            # Group pokemon_moves by version group
            pk_mv_vers = {}
            for pm in pokemon_moves:
                if pm.version_group_id not in pk_mv_vers:
                    pk_mv_vers[pm.version_group_id] = PokemonMoveVersion.fill(pm)

            # Return results in a consistent order
            return sorted(
                pk_mv_vers.values(),
                key=lambda pk_mv_ver: pk_mv_ver.level_learned_at
            )


class PokemonMoveVersion(ObjectType):
    level_learned_at = Int(description="The minimum level to learn the move.")
    move_learn_method_id = None
    move_learn_method = Field(
        lazy_import("pokemon_graphql.move_learn_method.types.MoveLearnMethod"),
        description="The method by which the move is learned."
    )
    version_group_id = None
    node = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group in which the move is learned."
    )

    def resolve_move_learn_method(self, info):
        return info.context.loaders.movelearnmethod.load(self.move_learn_method_id)

    def resolve_node(self, info):
        return info.context.loaders.versiongroup.load(self.version_group_id)

    class Meta:
        interfaces = (SimpleEdge, )

    @classmethod
    def fill(cls, data):
        obj = cls()
        obj.level_learned_at = data.level
        obj.move_learn_method_id = data.move_learn_method_id
        obj.version_group_id = data.version_group_id
        return obj


class PokemonStat(ObjectType):
    base_stat = Int(description="The base value of the stat.")
    effort = Int(
        name="effortPoints",
        description="The effort points (EV) the Pokémon has in the stat."
    )
    stat_id = None
    node = Field(
        lazy_import("pokemon_graphql.stat.types.Stat"),
        description="The stat the Pokémon has."
    )

    def resolve_node(self, info):
        return info.context.loaders.stat.load(self.stat_id)

    class Meta:
        interfaces = (SimpleEdge, )


class PokemonType(ObjectType):
    slot = Int(description="The order the Pokémon's types are listed in.")
    type_id = None
    node = Field(
        lazy_import("pokemon_graphql.type.types.Type"),
        description="The type the Pokémon has."
    )

    def resolve_node(self, info):
        return info.context.loaders.type.load(self.type_id)

    class Meta:
        interfaces = (SimpleEdge, )
