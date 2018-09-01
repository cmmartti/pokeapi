# -*- coding: utf-8 -*-
import json
from graphene import *
from graphene import relay

from .types import Pokemon
from ..base import BaseConnection, BaseOrder, BaseVersionGameIndex
from ..where import BaseWhere, TranslationSearch


class PokemonConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Pokemon


class PokemonOrdering(BaseOrder):
    sort = InputField(Enum('PokemonSort', [
            ("ORDER", "order"),
            ("HEIGHT", "height"),
            ("IS_DEFAULT", "is_default"),
            ("WEIGHT", "weight"),
            ("NAME", "name"),
        ]),
        description="The field to sort by."
    )


class PokemonWhere(BaseWhere):
    abilities = List(ID)
    base_experience__gt = Int(name="baseExperience_gt")
    height__gt = Int(name="height_gt")
    is_default = Boolean()
    moves = List(ID)
    name = Argument(TranslationSearch)
    types = List(ID)
    weight__gt = Int(name="weight_gt")
    species_color = ID(name="species_color")
    species_shape = ID(name="species_shape")
    species_generation = ID(name="species_generation")

    @classmethod
    def apply(cls, query_set, **where):

        abilities = where.pop("abilities", None)
        if abilities:
            for encoded_id in abilities:
                if encoded_id:
                    id = cls.get_id(encoded_id, "Ability", "abilities")
                    query_set = query_set.filter(pokemonability__ability_id=id)

        types = where.pop("types", None)
        if types:
            for encoded_id in types:
                if encoded_id:
                    id = cls.get_id(encoded_id, "Type", "types")
                    query_set = query_set.filter(pokemontype__type_id=id)

        moves = where.pop("moves", None)
        if moves:
            for encoded_id in moves:
                if encoded_id:
                    id = cls.get_id(encoded_id, "Move", "moves")
                    query_set = query_set.filter(pokemonmove__move_id=id)

        species_color = where.pop("species_color", None)
        if species_color:
            id = cls.get_id(species_color, "PokemonColor", "species_color")
            query_set = query_set.filter(pokemon_species__pokemon_color_id=id)

        species_shape = where.pop("species_shape", None)
        if species_shape:
            id = cls.get_id(species_shape, "PokemonShape", "species_shape")
            query_set = query_set.filter(pokemon_species__pokemon_shape_id=id)

        species_generation = where.pop("species_generation", None)
        if species_generation:
            id = cls.get_id(species_generation, "Generation", "species_generation")
            query_set = query_set.filter(pokemon_species__generation_id=id)

        name = where.pop("name", None)
        if name:
            if name.case_sensitive:
                query_set = query_set.filter(name__contains=name.query)
            else:
                query_set = query_set.filter(name__icontains=name.query)

        return super(PokemonWhere, cls).apply(query_set, **where)
