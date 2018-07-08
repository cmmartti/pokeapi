# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseGenerationGameIndex
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import BaseWhere, Where


class Type(ObjectType):
    """
    Types are properties for Pokémon and their moves. Each type has three properties: which types of Pokémon it is super effective against, which types of Pokémon it is not very effective against, and which types of Pokémon it is completely ineffective against.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: TypeName,
        description="The name of this type listed in different languages."
    )
    game_indices = List(
        lambda: TypeGameIndex,
        description="A list of game indices relevent to this item by generation."
    )
    generation_id = None
    generation = Field(
        lazy_import("pokemon_graphql.generation.types.Generation"),
        description="The generation this type was introduced in."
    )
    move_damage_class_id = None
    move_damage_class = Field(
        lazy_import("pokemon_graphql.move_damage_class.types.MoveDamageClass"),
        description="The class of damage inflicted by moves of this type."
    )
    pokemon = relay.ConnectionField(
        lambda: TypePokemonConnection,
        description="A list of details of Pokémon that have this type.",
        # where=Argument(lambda: TypePokemonWhere),
        order_by=Argument(lambda: TypePokemonOrder)
    )
    moves = relay.ConnectionField(
        lazy_import("pokemon_graphql.move.types.MoveConnection"),
        description="A list of moves that have this type.",
        where=Argument(Where),
        order_by=Argument(lazy_import("pokemon_graphql.move.types.MoveOrder"))
    )
    no_damage_to = List(
        lambda: Type,
        description="A list of types this type has no effect on."
    )
    half_damage_to = List(
        lambda: Type,
        description="A list of types this type is not very effective against."
    )
    double_damage_to = List(
        lambda: Type,
        description="A list of types this type is very effective against."
    )
    no_damage_from = List(
        lambda: Type,
        description="A list of types that have no effect on this type."
    )
    half_damage_from = List(
        lambda: Type,
        description="A list of types that are not very effective against this type."
    )
    double_damage_from = List(
        lambda: Type,
        description="A list of types that are very effective against this type."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.type_names.load(key)

    def resolve_game_indices(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.type_gameindices.load(key)

    def resolve_generation(self, info, **kwargs):
        return info.context.loaders.generation.load(self.generation_id)

    def resolve_move_damage_class(self, info, **kwargs):
        if not self.move_damage_class_id:
            return None
        return info.context.loaders.movedamageclass.load(self.move_damage_class_id)

    def resolve_pokemon(self, info, **kwargs):
        q = models.PokemonType.objects.filter(type_id=self.id)
        q = q.select_related('pokemon')
        # q = TypePokemonWhere.apply(q, **kwargs.get("where", {}))

        page = getPage(q, TypePokemonConnection.__name__, **kwargs)
        return TypePokemonConnection(
            edges=[
                TypePokemonConnection.Edge(
                    node=entry.pokemon,
                    slot=entry.slot,
                    cursor=page.get_cursor(entry)
                ) for entry in page
            ],
            page_info=page.page_info,
            total_count=page.total_count,
        )

    def resolve_moves(self, info, **kwargs):
        from ..move.types import MoveConnection

        q = models.Move.objects.filter(type_id=self.id)
        q = Where.apply(q, **kwargs.get("where", {}))
        return getConnection(q, MoveConnection, **kwargs)

    def resolve_no_damage_to(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.typeefficacies_by_damagetype.load(key).then(
            lambda res: [teff.target_type for teff in res if teff.damage_factor == 0]
        )

    def resolve_half_damage_to(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.typeefficacies_by_damagetype.load(key).then(
            lambda res: [teff.target_type for teff in res if teff.damage_factor == 50]
        )

    def resolve_double_damage_to(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.typeefficacies_by_damagetype.load(key).then(
            lambda res: [teff.target_type for teff in res if teff.damage_factor == 200]
        )

    def resolve_no_damage_from(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.typeefficacies_by_targettype.load(key).then(
            lambda res: [teff.damage_type for teff in res if teff.damage_factor == 0]
        )

    def resolve_half_damage_from(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.typeefficacies_by_targettype.load(key).then(
            lambda res: [teff.damage_type for teff in res if teff.damage_factor == 50]
        )

    def resolve_double_damage_from(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.typeefficacies_by_targettype.load(key).then(
            lambda res: [teff.damage_type for teff in res if teff.damage_factor == 200]
        )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.type.load(id)


class TypeConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Type


class TypeOrderField(Enum):
    """Properties by which type connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == TypeOrderField.NAME:
            return "Order by name."


class TypeOrder(BaseOrder):
    """Ordering options for type connections."""
    field = TypeOrderField(
        description="The field to order edges by.",
        required=True
    )


class TypeName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.typename.load(id)


class TypeGameIndex(BaseGenerationGameIndex):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.typegameindex.load(id)


from ..pokemon.types import Pokemon
class TypePokemonConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Pokemon

    class Edge:
        slot = Int(
            description="The order the Pokémon's types are listed in."
        )


class TypePokemonOrderField(Enum):
    """Properties by which type Pokémon connections can be ordered."""
    NAME = "name"
    SLOT = "slot"

    @property
    def description(self):
        if self == TypePokemonOrderField.NAME:
            return "Order by name."
        elif self == TypePokemonOrderField.SLOT:
            return "Order by type slot."


class TypePokemonOrder(BaseOrder):
    """Ordering options for type Pokémon connections."""
    field = TypePokemonOrderField(
        description="The field to order edges by.",
        required=True
    )

# class TypePokemonWhere(BaseWhere):
#     """Filtering options for Type Pokémon connections."""
#     pass
