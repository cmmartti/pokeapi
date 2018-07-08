# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from pokemon_v2 import models
from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseDescription
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList
from ..where import BaseWhere
from ..item_interface.connection import get_item_node


class EvolutionChain(ObjectType):
    """
    Evolution chains are essentially family trees. They start with the lowest stage within a family and detail evolution conditions for each as well as Pokémon they can evolve into up through the hierarchy.
    """

    baby_trigger_item_id = None
    baby_trigger_item = Field(
        lazy_import("pokemon_graphql.item_interface.types.ItemInterface"),
        description="The item that a Pokémon would be holding when mating that would trigger the egg hatching a baby Pokémon rather than a basic Pokémon."
    )
    chain = Field(
        lambda: ChainLink,
        description="The base chain link object. Each link contains evolution details for a Pokémon in the chain. Each link references the next Pokémon in the natural evolution order."
    )

    def resolve_baby_trigger_item(self, info):
        if not self.baby_trigger_item_id:
            return None
        return info.context.loaders.item.load(self.baby_trigger_item_id).then(
            lambda item: get_item_node(item)
        )

    def resolve_chain(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.evolutionchain_pokemonspecies.load(key).then(
            lambda data: EvolutionChain.get_chain(self, data)
        )

    @staticmethod
    def get_chain(root, data):
        for species in data:
            if species.evolves_from_species_id is None:
                chain_link = ChainLink()
                chain_link.evolution_chain_id = root.id
                chain_link.is_baby = species.is_baby
                chain_link.pokemon_species_id = species.id
                chain_link.species = species
                return chain_link
        return None

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.evolutionchain.load(id)


class EvolutionChainConnection(BaseConnection, relay.Connection):
    class Meta:
        node = EvolutionChain


class EvolutionChainOrderField(Enum):
    """Properties by which evolution chain connections can be ordered."""

    NAME = "name"

    @property
    def description(self):
        if self == EvolutionChainOrderField.NAME:
            return "Order by name."


class EvolutionChainOrder(BaseOrder):
    """Ordering options for evolution chain connections."""
    field = EvolutionChainOrderField(
        description="The field to order edges by.",
        required=True
    )


class EvolutionChainWhere(BaseWhere):
    """Filtering options for evolution chain connections."""

    pokemonspecies__id = ID(
        name="pokemonSpecies_ID",
        description="Filter by chains that have this Pokémon species."
    )

    @classmethod
    def apply(cls, query_set, **where):
        pokemonspecies__id = where.pop("pokemonspecies__id", None)
        if pokemonspecies__id:
            id = cls.get_id(pokemonspecies__id, "PokemonSpecies", "pokemonSpecies_ID")
            query_set = query_set.filter(pokemonspecies__id=id)

        return query_set


class ChainLink(ObjectType):
    evolution_chain_id = None
    is_baby = Boolean(
        description="Whether or not this link is for a baby Pokémon. This would only ever be true on the base link."
    )
    pokemon_species_id = None
    species = Field(
        lazy_import("pokemon_graphql.pokemon_species.types.PokemonSpecies"),
        description="The Pokémon species at this point in the evolution chain."
    )
    conditions = List(
        lambda: EvolutionDetail,
        description="All details regarding the specific details of the referenced Pokémon species evolution."
    )
    evolves_to = List(lambda: ChainLink, description="A List of chain objects.")

    def resolve_conditions(self, info, **kwargs):
        key = LoaderKey(self.pokemon_species_id, **kwargs)
        return info.context.loaders.pokemonevolutions_by_pokemonspecies.load(key)

    def resolve_evolves_to(self, info, **kwargs):
        key = LoaderKey(self.evolution_chain_id, **kwargs)
        return info.context.loaders.evolutionchain_pokemonspecies.load(key).then(
            lambda data: ChainLink.get_chains(self, data)
        )

    @staticmethod
    def get_chains(root, data):
        data.sort(key=lambda species: species.order)
        data.sort(key=lambda species: species.id)
        chains = []
        for species in data:
            if species.evolves_from_species_id == root.pokemon_species_id:
                chain_link = ChainLink()
                chain_link.evolution_chain_id = root.evolution_chain_id
                chain_link.is_baby = species.is_baby
                chain_link.pokemon_species_id = species.id
                chain_link.species = species
                chains.append(chain_link)
        return chains


class EvolutionDetail(ObjectType):
    evolution_item_id = None
    item = Field(
        lazy_import("pokemon_graphql.item_interface.types.ItemInterface"),
        description="The item required to cause evolution this into Pokémon species."
    )
    def resolve_item(self, info):
        if not self.evolution_item_id:
            return None
        return info.context.loaders.item.load(self.evolution_item_id).then(
            lambda item: get_item_node(item)
        )

    gender_id = None
    gender = Field(
        lazy_import("pokemon_graphql.gender.types.Gender"),
        description="The id of the gender of the evolving Pokémon species must be in order to evolve into this Pokémon species."
    )
    def resolve_gender(self, info):
        if not self.gender_id:
            return None
        return info.context.loaders.gender.load(self.gender_id)

    held_item_id = None
    held_item = Field(
        lazy_import("pokemon_graphql.item_interface.types.ItemInterface"),
        description="The item the evolving Pokémon species must be holding during the evolution trigger event to evolve into this Pokémon species."
    )
    def resolve_held_item(self, info):
        if not self.held_item_id:
            return None
        return info.context.loaders.item.load(self.held_item_id).then(
            lambda item: get_item_node(item)
        )

    known_move_id = None
    known_move = Field(
        lazy_import("pokemon_graphql.move.types.Move"),
        description="The move that must be known by the evolving Pokémon species during the evolution trigger event in order to evolve into this Pokémon species."
    )
    def resolve_known_move(self, info):
        if not self.known_move_id:
            return None
        return info.context.loaders.move.load(self.known_move_id)

    known_move_type_id = None
    known_move_type = Field(
        lazy_import("pokemon_graphql.type.types.Type"),
        description="The evolving Pokémon species must know a move with this type during the evolution trigger event in order to evolve into this Pokémon species."
    )
    def resolve_known_move_type(self, info):
        if not self.known_move_type_id:
            return None
        return info.context.loaders.movetype.load(self.known_move_type_id)

    location_id = None
    location = Field(
        lazy_import("pokemon_graphql.location.types.Location"),
        description="The location the evolution must be triggered at.."
    )
    def resolve_location(self, info):
        if not self.location_id:
            return None
        return info.context.loaders.location.load(self.location_id)

    min_level = Int(
        description="The minimum required level of the evolving Pokémon species to evolve into this Pokémon species."
    )
    min_happiness = Int(
        description="The minimum required level of happiness the evolving Pokémon species to evolve into this Pokémon species."
    )
    min_beauty = Int(
        description="The minimum required level of beauty the evolving Pokémon species to evolve into this Pokémon species."
    )
    min_affection = Int(
        description="The minimum required level of affection the evolving Pokémon species to evolve into this Pokémon species."
    )
    needs_overworld_rain = Boolean(
        description="Whether or not it must be raining in the overworld to cause evolution this Pokémon species."
    )

    party_species_id = None
    party_species = Field(
        lazy_import("pokemon_graphql.pokemon_species.types.PokemonSpecies"),
        description="The Pokémon species that must be in the players party in order for the evolving Pokémon species to evolve into this Pokémon species."
    )
    def resolve_party_species(self, info):
        if not self.party_species_id:
            return None
        return info.context.loaders.pokemonspecies.load(self.party_species_id)

    party_type_id = None
    party_species_type = Field(
        lazy_import("pokemon_graphql.type.types.Type"),
        description="The player must have a Pokémon of this type in their party during the evolution trigger event in order for the evolving Pokémon species to evolve into this Pokémon species."
    )
    def resolve_party_species_type(self, info):
        if not self.party_type_id:
            return None
        return info.context.loaders.type.load(self.party_type_id)

    relative_physical_stats = Int(
        description="The required relation between the Pokémon's Attack and Defense stats. 1 means Attack > Defense. 0 means Attack = Defense. -1 means Attack < Defense."
    )
    time_of_day = String(description="The required time of day. Day or night.")

    trade_species_id = None
    trade_species = Field(
        lazy_import("pokemon_graphql.pokemon_species.types.PokemonSpecies"),
        description="Pokémon species for which this one must be traded."
    )
    def resolve_trade_species(self, info):
        if not self.trade_species_id:
            return None
        return info.context.loaders.pokemonspecies.load(self.trade_species_id)

    evolution_trigger_id = None
    trigger = Field(
        lazy_import("pokemon_graphql.evolution_trigger.types.EvolutionTrigger"),
        description="The type of event that triggers evolution into this Pokémon species."
    )
    def resolve_trigger(self, info):
        return info.context.loaders.evolutiontrigger.load(self.evolution_trigger_id)

    turn_upside_down = Boolean(
        description="Whether or not the 3DS needs to be turned upside-down as this Pokémon levels up."
    )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemonevolution.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls()
        obj.id = data.id
        obj.evolution_item_id = data.evolution_item_id
        obj.evolution_trigger_id = data.evolution_trigger_id
        obj.gender_id = data.gender_id
        obj.held_item_id = data.held_item_id
        obj.known_move_id = data.known_move_id
        obj.known_move_type_id = data.known_move_type_id
        obj.location_id = data.location_id
        obj.min_level = data.min_level
        obj.min_happiness = data.min_happiness
        obj.min_beauty = data.min_beauty
        obj.min_affection = data.min_affection
        obj.needs_overworld_rain = data.needs_overworld_rain
        obj.party_species_id = data.party_species_id
        obj.party_type_id = data.party_type_id
        obj.relative_physical_stats = data.relative_physical_stats
        obj.time_of_day = data.time_of_day
        obj.trade_species_id = data.trade_species_id
        obj.turn_upside_down = data.turn_upside_down

        return obj
