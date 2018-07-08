from graphene import *

from ..interfaces import RelayNode, SimpleEdge


class PokemonSpeciesPokedexEntry(ObjectType):
    pokedex_number = Int(
        name="entryNumber",
        description="The index number within the Pokédex."
    )
    pokedex_id = None
    node = Field(
        lazy_import("pokemon_graphql.pokedex.types.Pokedex"),
        description="The Pokédex the referenced Pokémon species can be found in."
    )

    def resolve_node(self, info):
        return info.context.loaders.pokedex.load(self.pokedex_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.pokemondexnumber.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, pokedex_number=data.pokedex_number)
        obj.pokedex_id = data.pokedex_id
        return obj


class PokemonSpeciesPalParkEncounter(ObjectType):
    base_score = Int(
        description="The base score given to the player when the referenced Pokémon is caught during a pal park run."
    )
    rate = Int(
        description="The base rate for encountering the referenced Pokémon in this pal park area."
    )
    pal_park_area_id = None
    node = Field(
        lazy_import("pokemon_graphql.pal_park_area.types.PalParkArea"),
        description="The pal park area where this encounter happens."
    )

    def resolve_node(self, info):
        return info.context.loaders.palparkarea.load(self.pal_park_area_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.palpark.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, base_score=data.base_score, rate=data.rate)
        obj.pal_park_area_id = data.pal_park_area_id
        return obj
