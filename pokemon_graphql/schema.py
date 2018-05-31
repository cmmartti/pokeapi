# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from promise import Promise
from graphql_relay.connection.connectiontypes import Edge
from graphene import ID, Int, String, Boolean, Field, List, Enum
from graphene import ObjectType, Interface, Schema, relay
from graphene import InputObjectType, Argument, InputField

from .loader_key import LoaderKey
from .connections import getConnection, getPage
from pokemon_v2 import models


# ObjectType attributes without a String, Field, List, etc. and that are set to None are
# _private_. They cannot be accessed by the client. They are used to simplify resolvers.
# The default resolver matches field names with attributes with the same name in the
# initial data, which given the initial data is usually a Django model often includes
# the ID of the field we might need. Resolvers can then use that private attribute
# to resolve other fields.


# Base field types
class RelayNode(relay.Node):
    class Meta:
        name = "Node"
        description = "An object with an ID."

    # Let us assume that the class name of the object (Django model)
    # returned by the resolver is also the name of the GraphQL object type
    # When this assumption is not true, the `get_node` method on the type will
    # explicity return the correct type (look for the `fill` method).
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

class BaseNode(ObjectType):
    class Meta:
        interfaces = (RelayNode, )

class BaseConnection(object):
    totalCount = Int(
        description="Identifies the total count of items in the connection."
    )


# Field Argument Types
class OrderDirection(Enum):
    ASC = "asc"
    DESC = "desc"

    @property
    def description(self):
        if self == OrderDirection.ASC:
            return "Specifies an ascending order for a given orderBy argument."
        if self == OrderDirection.DESC:
            return "Specifies an descending order for a given orderBy argument."


class Order(InputObjectType):
    """Base ordering options for connections."""
    direction = OrderDirection(description="The ordering direction.", required=True)


class Where(InputObjectType):
    """Base filtering options for connections."""
    name = String(description="The full name of a resource.")


#######################################
class GenerationGameIndex(ObjectType):
    """???"""

    game_index = Int(description='The internal id of a resource within game data.')
    generation = Field(
        lambda: Generation,
        description='The generation relevent to this game index.'
    )


#######################################
class Encounter(ObjectType):
    '''
    An encounter is a set of conditions that must be met in order to meet a particular Pokémon, and the likelihood that the encounter will occur if the conditions are met.
    '''

    chance = Int(description='The percent chance that this encounter will occur.')
    # condition_values = List(
    #     lambda: EncounterConditionValue,
    #     description='A list of condition values that must be in effect for this encounter to occur.'
    # )
    max_level = Int(description='The highest level the Pokémon can be encountered at.')
    encounter_method_id = None
    method = Field(
        lambda: EncounterMethod,
        description='The method by which this encounter happens.'
    )
    min_level = Int(description='The lowest level the Pokémon can be encountered at.')

    def resolve_condition_values(self, info):
        return info.context.loaders.encounterconditionvalues_by_encounter(self.id)

    def resolve_method(self, info):
        return info.context.loaders.encountermethod.load(self.encounter_method_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encounter_with_encounterslot.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        assert isinstance(data, models.Encounter)
        slot = data.encounter_slot
        obj = cls()
        obj.id = data.id
        obj.chance = slot.rarity
        obj.encounter_method_id = slot.encounter_method_id
        obj.max_level = data.max_level
        obj.min_level = data.min_level
        return obj


class EncounterConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Encounter


class EncounterOrderField(Enum):
    """Properties by which encounter connections can be ordered."""
    CHANCE = "chance"
    MAX_LEVEL = "max_level"
    MIN_LEVEL = "min_level"

    @property
    def description(self):
        if self == EncounterOrderField.CHANCE:
            return "Order encounters by the percent chance that each will occur."
        if self == EncounterOrderField.MAX_LEVEL:
            return "Order encounters by the highest level the Pokémon can be encountered at."
        if self == EncounterOrderField.MIN_LEVEL:
            return "Order encounters by the lowest level the Pokémon can be encountered at."


class EncounterOrder(Order):
    """Ordering options for encounter connections."""
    field = EncounterOrderField(
        description="The field to order encounters by.",
        required=True
    )


#######################################
class VersionEncounterDetail(ObjectType):
    """
    A list of encounters for a specific Location Area, Pokémon, and Version.
    """
    location_area_id = None
    pokemon_id = None
    maxChance = Int(description='The total percentage of all encounter potential.')
    encounter_details = relay.ConnectionField(
        lambda: EncounterConnection,
        description='A list of encounters and their specifics.',
        where=Argument(lambda: Where), order_by=Argument(lambda: EncounterOrder)
    )
    version_id = None
    version = Field(
        lambda: Version,
        description='The game version this encounter happens in.')

    def resolve_version(self, info):
        return info.context.loaders.version.load(self.version_id)

    def resolve_encounter_details(self, info, **kwargs):
        q = models.Encounter.objects.all()
        q = q.filter(location_area_id=self.location_area_id)
        q = q.filter(pokemon_id=self.pokemon_id)
        q = q.filter(version_id=self.version_id)
        q = q.select_related('encounter_slot')
        return getConnection(q, EncounterConnection, Encounter.fill, **kwargs)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, encoded_id):

        # There is no model counterpart for this schema type, hence the composite ID
        id = VersionEncounterID.decode(encoded_id)

        q = models.Encounter.objects.all()
        q = q.filter(location_area_id=id.location_area_id)
        q = q.filter(pokemon_id=id.pokemon_id)
        q = q.filter(version_id=id.version_id)
        q = q.select_related('encounter_slot')
        return cls.fill(q, id)

    @classmethod
    def fill(cls, data, id):

        obj = cls(id=id)
        obj.location_area_id = id.location_area_id
        obj.pokemon_id = id.pokemon_id
        obj.version_id = id.version_id

        maxChance = 0
        for encounter in data:
            maxChance += encounter.encounter_slot.rarity
        obj.maxChance = maxChance

        return obj


class VersionEncounterID(object):
    """A composite ID."""

    def __init__(self, location_area_id, pokemon_id, version_id):
        self.location_area_id = location_area_id
        self.pokemon_id = pokemon_id
        self.version_id = version_id

    def encode(self):
        return str(self.location_area_id) + "/" + str(self.pokemon_id) + "/" + str(self.version_id)

    @classmethod
    def decode(cls, encoded):
        area_id, poke_id, vers_id = encoded.split("/")
        return cls(area_id, poke_id, vers_id)

    def __str__(self):
        return self.encode()


#######################################
class EncounterMethod(ObjectType):
    """
    Methods by which the player might encounter Pokémon in the wild, e.g., walking in tall grass. Check out [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Wild_Pok%C3%A9mon) for greater detail.
    """

    name = String(description="The name of this resource.")
    names = NameList(
        lambda: EncounterMethodName,
        description="The name of this encounter method listed in different languages."
    )
    order = Int(description="A good value for sorting.")

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.encountermethod_names.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encountermethod.load(id)


class EncounterMethodConnection(BaseConnection, relay.Connection):
    class Meta:
        node = EncounterMethod


class EncounterMethodOrderField(Enum):
    """Properties by which encounter method connections can be ordered."""
    NAME = "name"
    ORDER = "order"

    @property
    def description(self):
        if self == EncounterMethodOrderField.NAME:
            return "Order encounter methods by name."
        if self == EncounterMethodOrderField.ORDER:
            return "Order encounter methods by the standard order."


class EncounterMethodOrder(Order):
    """Ordering options for encounter method connections."""
    field = EncounterMethodOrderField(
        description="The field to order encounter methods by.",
        required=True
    )


class EncounterMethodName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.encountermethodname.load(id)


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


class LanguageConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Language


class LanguageOrderField(Enum):
    """Properties by which language connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == LanguageOrderField.NAME:
            return "Order languages by name."


class LanguageOrder(Order):
    """Ordering options for language connections."""
    field = LanguageOrderField(
        description="The field to order languages by.",
        required=True
    )


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
        return info.context.loaders.languagename.load(id)


#######################################
class Location(ObjectType):
    """
    Locations that can be visited within the games. Locations make up sizable portions of regions, like cities or routes.
    """

    name = String(description="The name of this resource.")
    names = NameList(
        lambda: LocationName,
        description="The name of this location listed in different languages."
    )
    region_id = None
    # region = Field(
    #     lambda: Region,
    #     description="The region this location can be found in."
    # )
    game_indices = List(
        lambda: LocationGameIndex,
        description="A list of game indices relevent to this location by generation."
    )
    # areas = List(
    #     lambda: LocationArea,
    #     description="Areas that can be found within this location."
    # )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.location_names.load(key)

    def resolve_region(self, info, **kwargs):
        return info.context.loaders.region.load(self.region_id)

    def resolve_game_indices(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.location_gameindices.load(key)

    def resolve_areas(self, info, **kwargs):
        key = LoaderKey(self.id, kwargs)
        return info.context.loaders.locationareas_by_location.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.location.load(id)


class LocationConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Location


class LocationOrderField(Enum):
    """Properties by which location connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == LocationOrderField.NAME:
            return "Order locations by name."


class LocationOrder(Order):
    """Ordering options for location connections."""
    field = LocationOrderField(
        description="The field to order locations by.",
        required=True
    )


class LocationName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationname.load(id)


class LocationGameIndex(GenerationGameIndex):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationgameindex.load(id)


#######################################
class Region(ObjectType):
    """
    Regions that can be visited within the games. Regions make up sizable portions of regions, like cities or routes.
    """

    name = String(description="The name of this resource.")
    names = NameList(
        lambda: RegionName,
        description="The name of this region listed in different languages."
    )
    main_generation = Field(
        lambda: Generation,
        description="The generation this region was introduced in."
    )
    locations = relay.ConnectionField(
        lambda: LocationConnection,
        description="A list of locations that can be found in this region.",
        where=Argument(Where), order_by=Argument(LocationOrder)
    )
    # pokedexes = List(
    #     lambda: Pokedex,
    #     description="A lists of pokédexes that catalogue Pokémon in this region."
    # )
    version_groups = List(
        lambda: VersionGroup,
        description="A list of version groups where this region can be visited."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.region_names.load(key)

    def resolve_main_generation(self, info, **kwargs):
        return info.context.loaders.generation_by_region.load(self.id)

    def resolve_locations(self, info, **kwargs):
        q = models.Location.objects.filter(region_id=self.id)
        return getConnection(q, LocationConnection, **kwargs)

    def resolve_pokedexes(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.pokedexes_by_region.load(key)

    def resolve_version_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versiongroups_by_region.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.region.load(id)


class RegionConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Region


class RegionOrderField(Enum):
    """Properties by which region connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == RegionOrderField.NAME:
            return "Order regions by name."


class RegionOrder(Order):
    """Ordering options for region connections."""
    field = RegionOrderField(
        description="The field to order regions by.",
        required=True
    )


class RegionName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.regionname.load(id)


#######################################
class LocationArea(ObjectType):
    '''
    Location areas are sections of areas, such as floors in a building or cave. Each area has its own set of possible Pokémon encounters.
    '''
    name = String(description="The name of this resource.")
    names = NameList(
        lambda: LocationAreaName,
        description="The name of this location area listed in different languages."
    )
    game_index = Int(description="The internal id of an API resource within game data.")
    location_id = None
    location = Field(
        lambda: Location,
        description="The location this area can be found in"
    )
    encounter_method_rates = List(
        lambda: EncounterMethodRate,
        description="A list of methods in which Pokémon may be encountered in this area and how likely the method will occur depending on the version of the game."
    )
    pokemon_encounters = relay.ConnectionField(
        lambda: PokemonEncounterConnection,
        description="A list of Pokémon that can be encountered in this area along with version specific details about the encounter."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.locationarea_names.load(key)

    def resolve_location(self, info, **kwargs):
        return info.context.loaders.location.load(self.location_id)

    def resolve_encounter_method_rates(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.locationareaencounterrates_by_locationarea.load(key)

    def resolve_pokemon_encounters(self, info, **kwargs):
        q = models.Pokemon.objects.all()
        q = q.filter(encounter__location_area_id=self.id).distinct()
        return getConnection(
            q,
            PokemonEncounterConnection,
            lambda pokemon: PokemonEncounter.fill(
                PokemonEncounterID(self.id, pokemon.id)
            ),
            **kwargs
        )

    class Meta:
        interfaces = (RelayNode, )


    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationarea.load(id)


class LocationAreaConnection(BaseConnection, relay.Connection):
    class Meta:
        node = LocationArea


class LocationAreaOrderField(Enum):
    """Properties by which location area connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == LocationAreaOrderField.NAME:
            return "Order location areas by name."


class LocationAreaOrder(Order):
    """Ordering options for location area connections."""
    field = LocationAreaOrderField(
        description="The field to order location areas by.",
        required=True
    )


class LocationAreaName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationareaname.load(id)


class PokemonEncounter(ObjectType):
    """
    A list of encouters by version for a specific Location Area and Pokémon.
    """

    location_area_id = None
    pokemon_id = Int()
    # pokemon = Field(lambda: Pokemon, description="The Pokémon being encountered.")
    version_details = List(
        lambda: VersionEncounterDetail,
        description="A list of versions and encounters with Pokémon that might happen in the referenced location area."
    )

    def resolve_pokemon(self, info):
        return info.context.loaders.pokemon.load(self.pokemon_id)

    def resolve_version_details(self, info):
        encounters = models.Encounter.objects.all()
        encounters = encounters.select_related('encounter_slot')
        encounters = encounters.filter(location_area_id=self.location_area_id)
        encounters = encounters.filter(pokemon_id=self.pokemon_id)

        # Group encounters by version
        v_encounters = {}
        for e in encounters:
            if e.version_id not in v_encounters:
                v_encounters[e.version_id] = []
            v_encounters[e.version_id].append(e)

        version_details = []
        for v_id, enctrs in v_encounters.iteritems():
            id = VersionEncounterID(self.location_area_id, self.pokemon_id, v_id)
            version_detail = VersionEncounterDetail.fill(enctrs, id)
            version_details.append(version_detail)
        return version_details

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        # No database calls here because all scalar data is encoded in the composite ID
        return cls.fill(PokemonEncounterID.decode(id))

    @classmethod
    def fill(cls, id):
        obj = cls(id=id)
        obj.location_area_id = id.location_area_id
        obj.pokemon_id = id.pokemon_id
        return obj


class PokemonEncounterID(object):
    """A composite ID."""

    def __init__(self, location_area_id, pokemon_id):
        self.location_area_id = location_area_id
        self.pokemon_id = pokemon_id

    def encode(self):
        return str(self.location_area_id) + "/" + str(self.pokemon_id)

    @classmethod
    def decode(cls, encoded):
        area_id, poke_id = encoded.split("/")
        return cls(area_id, poke_id)

    def __str__(self):
        return self.encode()


class PokemonEncounterConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonEncounter


class EncounterVersionDetails(ObjectType):
    rate = Int(description="The chance of an encounter to occur.")
    version_id = None
    version = Field(
        lambda: Version,
        description="The version of the game in which the encounter can occur with the given chance."
    )

    def resolve_version(self, info, **kwargs):
        return info.context.loaders.version.load(self.version_id)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationareaencounterrate.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls()
        obj.id = data.id
        obj.rate = data.rate
        obj.version_id = data.version_id
        return obj


class EncounterMethodRate(ObjectType):
    location_area_id = None
    encounter_method_id = None
    encounter_method = Field(
        lambda: EncounterMethod,
        description="The method in which Pokémon may be encountered in an area."
    )
    version_details = List(
        lambda: EncounterVersionDetails,
        description="The chance of the encounter to occur on a version of the game."
    )

    def resolve_encounter_method(self, info):
        return info.context.loaders.encountermethod.load(self.encounter_method_id)

    def resolve_version_details(self, info, **kwargs):
        key = LoaderKey(self.location_area_id, **kwargs)
        return info.context.loaders.locationareaencounterrates_by_locationarea.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.locationareaencounterrate.load(id).then(cls.fill)

    @classmethod
    def fill(cls, data):
        obj = cls()
        obj.id = data.id
        obj.location_area_id = data.location_area_id
        obj.encounter_method_id = data.encounter_method_id
        return obj


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
    # abilities = relay.ConnectionField(
    #     lambda: Ability,
    #     description="A list of abilities that were introduced in this generation.",
    #     where=Argument(lambda: Where), order_by=Argument(lambda: AbilityOrder)
    # )
    region_id = None
    main_region = Field(
        lambda: Region,
        description="The main region travelled in this generation."
    )
    # moves = relay.ConnectionField(
    #     lambda: Move,
    #     description="A list of moves that were introduced in this generation.",
    #     where=Argument(lambda: Where), order_by=Argument(lambda: MoveOrder)
    # )
    # pokemon_species = relay.ConnectionField(
    #     lambda: PokemonSpecies,
    #     description="A list of Pokémon species that were introduced in this generation.",
    #     where=Argument(lambda: Where), order_by=Argument(lambda: PokemonSpeciesOrder)
    # )
    # types = List(
    #     lambda: Type,
    #     description="A list of types that were introduced in this generation."
    # )
    version_groups = List(
        lambda: VersionGroup,
        description="A list of version groups that were introduced in this generation."
    )

    def resolve_names(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.generation_names.load(key)

    def resolve_abilities(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.abilities_by_generation.load(key)

    # def resolve_abilities(self, info, **kwargs):
    #     q = models.Ability.objects.all()
    #     return getConnection(q, AbilityConnection, **kwargs)

    def resolve_main_region(self, info, **kwargs):
        return info.context.loaders.region.load(self.region_id)

    # def resolve_moves(self, info, **kwargs):
    #     q = models.Move.objects.all()
    #     return getConnection(q, MoveConnection, **kwargs)

    # def resolve_pokemon_species(self, info, **kwargs):
    #     q = models.PokemonSpecies.objects.all()
    #     return getConnection(q, PokemonSpeciesConnection, **kwargs)

    def resolve_types(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.types_by_generation.load(key)

    def resolve_version_groups(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.versiongroups_by_generation.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.generation.load(id)


class GenerationConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Generation


class GenerationOrderField(Enum):
    """Properties by which generation connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == GenerationOrderField.NAME:
            return "Order generations by name."


class GenerationOrder(Order):
    """Ordering options for generation connections."""
    field = GenerationOrderField(
        description="The field to order generations by.",
        required=True
    )


class GenerationWhere(Where):
    """Filtering options for generation connections."""
    pass


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


class VersionConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Version


class VersionName(Name):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.versionname.load(id)


class VersionOrderField(Enum):
    """Properties by which version connections can be ordered."""
    NAME = "name"

    @property
    def description(self):
        if self == VersionOrderField.NAME:
            return "Order version groups by name."


class VersionOrder(Order):
    """Ordering options for version connections."""
    field = VersionOrderField(
        description="The field to order versions by.",
        required=True
    )


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


class VersionGroupConnection(BaseConnection, relay.Connection):
    class Meta:
        node = VersionGroup


class VersionGroupOrderField(Enum):
    """Properties by which version group connections can be ordered."""
    ORDER = "order"
    NAME = "name"

    @property
    def description(self):
        if self == VersionGroupOrderField.ORDER:
            return "Order version groups by standard order."
        if self == VersionGroupOrderField.NAME:
            return "Order version groups by name."


class VersionGroupOrder(Order):
    """Ordering options for version group connections."""
    field = VersionGroupOrderField(
        description="The field to order version groups by.",
        required=True
    )


#######################################
# Root Query

class Query(ObjectType):
    """The root query node."""

    node = RelayNode.Field(description="Fetches an object given its ID.")
    encounter_methods = relay.ConnectionField(
        EncounterMethodConnection,
        description="A list of methods by which a player might encounter Pokémon in the wild.",
        where=Argument(Where), order_by=Argument(EncounterMethodOrder)
    )
    languages = relay.ConnectionField(
        LanguageConnection,
        description="A list of languages used for translations of resource information.",
        where=Argument(Where), order_by=Argument(LanguageOrder)
    )
    generations = relay.ConnectionField(
        GenerationConnection,
        description="A list of generations (groupings of games based on the Pokémon they include).",
        where=Argument(Where), order_by=Argument(GenerationOrder)
    )
    versions = relay.ConnectionField(
        VersionConnection,
        description="A list of versions of the games, e.g., Red, Blue or Yellow.",
        where=Argument(Where), order_by=Argument(VersionOrder)
    )
    version_groups = relay.ConnectionField(
        VersionGroupConnection,
        description="A list of version groups (highly similar versions of the games).",
        where=Argument(Where), order_by=Argument(VersionGroupOrder)
    )
    locations = relay.ConnectionField(
        LocationConnection,
        description="A list of locations that can be visited within games.",
        where=Argument(Where), order_by=Argument(LocationOrder)
    )
    location_areas = relay.ConnectionField(
        LocationAreaConnection,
        description="A list of location areas that can be visited within games.",
        where=Argument(Where), order_by=Argument(LocationAreaOrder)
    )
    regions = relay.ConnectionField(
        RegionConnection,
        description="A list of regions (organized areas) of the Pokémon world.",
        where=Argument(Where), order_by=Argument(RegionOrder)
    )

    def resolve_encounter_methods(self, info, **kwargs):
        q = models.EncounterMethod.objects.all()
        return getConnection(q, EncounterMethodConnection, **kwargs)

    def resolve_languages(self, info, **kwargs):
        q = models.Language.objects.all()
        return getConnection(q, LanguageConnection, **kwargs)

    def resolve_generations(self, info, **kwargs):
        q = models.Generation.objects.all()
        return getConnection(q, GenerationConnection, **kwargs)

    def resolve_versions(self, info, **kwargs):
        q = models.Version.objects.all()
        return getConnection(q, VersionConnection, **kwargs)

    def resolve_version_groups(self, info, **kwargs):
        q = models.VersionGroup.objects.all()
        return getConnection(q, VersionGroupConnection, **kwargs)

    def resolve_locations(self, info, **kwargs):
        q = models.Location.objects.all()
        return getConnection(q, LocationConnection, **kwargs)

    def resolve_location_areas(self, info, **kwargs):
        q = models.LocationArea.objects.all()
        return getConnection(q, LocationAreaConnection, **kwargs)

    def resolve_regions(self, info, **kwargs):
        q = models.Region.objects.all()
        return getConnection(q, RegionConnection, **kwargs)


schema = Schema(query=Query, auto_camelcase=True)
