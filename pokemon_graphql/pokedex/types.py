# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class Pokedex(ObjectType):
    """
    A Pokédex is a handheld electronic encyclopedia device; one which is capable of recording and retaining information of the various Pokémon in a given region with the exception of the national dex and some smaller dexes related to portions of a region. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Pokedex) for greater detail.
    """

    name = String(description="The name of this resource.")
    is_main_series = Boolean(description="Whether or not this Pokédex originated in the main series of the video games.")
    descriptions = TranslationList(
        lambda: PokedexDescription,
        description="The description of this Pokédex listed in different languages."
    )
    names = TranslationList(
        lambda: PokedexName,
        description="The name of this Pokédex listed in different languages."
    )
    pokemon_entries = relay.ConnectionField(
        lambda: PokedexEntryConnection,
        description="A list of Pokémon catalogued in this Pokédex and their indexes.",
        order_by=Argument(List(lambda: PokedexEntryOrdering))
    )


    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokedex_descriptions.load(key)

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokedex_names.load(key)

    def resolve_pokemon_entries(self, info, **kwargs):
        q = models.PokemonDexNumber.objects.filter(pokedex_id=self.id)
        q = q.select_related('pokemon_species')

        page = getPage(q, PokedexEntryConnection.__name__, **kwargs)
        edges = []
        for entry in page:
            edges.append(PokedexEntryConnection.Edge(
                node=entry.pokemon_species,
                entry_number=entry.pokedex_number,
                cursor=page.get_cursor(entry)
            ))
        return PokedexEntryConnection(
            edges=edges,
            page_info=page.page_info,
            total_count=page.total_count,
        )


    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokedex.load(id)


class PokedexConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Pokedex


class PokedexOrdering(BaseOrder):
    sort = InputField(
        Enum('PokedexSort', [("IS_MAIN_SERIES", "is_main_series"), ("NAME", "name")]),
        description="The field to sort by."
    )


class PokedexName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokedexname.load(id)
        node = Pokedex


class PokedexDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokedexdescription.load(id)


from ..pokemon_species.types import PokemonSpecies
class PokedexEntryConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonSpecies

    class Edge:
        entry_number = Int(
            description="The index of this Pokémon species entry within the Pokédex."
        )


class PokedexEntryOrdering(BaseOrder):
    sort = InputField(
        Enum('PokedexEntrySort', [("ENTRY_NUMBER", "pokedex_number")]),
        description="The field to sort by."
    )
