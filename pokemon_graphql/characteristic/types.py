# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..loader_key import LoaderKey
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseDescription
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import Where


class Characteristic(ObjectType):
    """
    Characteristics indicate which stat contains a Pokémon's highest [IV (individual value)](https://bulbapedia.bulbagarden.net/wiki/Individual_values). A Pokémon's Characteristic is determined by the remainder of its highest IV divided by 5 (gene_modulo). Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Characteristic) for greater detail.
    """

    descriptions = TranslationList(
        lambda: CharacteristicDescription,
        description="The description of this characteristic listed in different languages."
    )
    gene_mod_5 = Int(
        name="geneModulo",
        description="The remainder of the highest stat/IV divided by 5."
    )
    stat_id = None
    highest_stat = Field(
        lazy_import("pokemon_graphql.stat.types.Stat"),
        description="The stat that contains a Pokémon's highest [IV (indivual value)](https://bulbapedia.bulbagarden.net/wiki/Individual_values)."
    )
    possible_values = List(
        Int,
        description="The possible values of the highest stat that would result in a Pokémon recieving this characteristic when divided by 5."
    )

    def resolve_descriptions(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.characteristic_descriptions.load(key)

    def resolve_possible_values(self, info):
        mod = self.gene_mod_5
        values = []
        while (mod <= 30):
            values.append(mod)
            mod += 5
        return values

    def resolve_highest_stat(self, info):
        return info.context.loaders.stat.load(self.stat_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.characteristic.load(id)


class CharacteristicConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Characteristic


class CharacteristicOrderField(Enum):
    """Properties by which characteristic connections can be ordered."""
    NAME = "name"
    GENE_MODULO = "gene_mod_5"

    @property
    def description(self):
        if self == CharacteristicOrderField.NAME:
            return "Order by name."
        if self == CharacteristicOrderField.GENE_MODULO:
            return "Order by the remainder of the highest stat divided by 5."


class CharacteristicOrder(BaseOrder):
    """Ordering options for characteristic connections."""
    field = CharacteristicOrderField(
        description="The field to order edges by.",
        required=True
    )


class CharacteristicDescription(BaseDescription):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.characteristicdescription.load(id)
