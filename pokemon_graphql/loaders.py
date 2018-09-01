from promise import Promise
from promise.dataloader import DataLoader
from django.db.models import Q

from pokemon_v2.models import *
from .loader_util import (
    divide_by_key,
    get_relations,
    add_filters,
)

"""
Data loaders batch and cache requests to the database. Each request gets a new instance
of Loaders, so this is per-request only (see middleware for the specifics). Each data
loader returns a list of Django model objects. Any manipulation occurs elsewhere in the
program (in field resolvers).

To use a data loader, instantiate a Loaders object (or get it from the context), then
call the `load()` method on a specific loader, passing in a key. Data loaders take one
of two kinds of keys: simple integer IDs, or instances of LoaderKey. Loaders that return
simple objects take integer IDs, while loaders that return lists of objects take
LoaderKey instances, allowing for complex filtering. The loader will return a Promise.

For more information about DataLoader, see https://github.com/syrusakbary/aiodataloader.
"""

class Loaders(object):
    """Create a new set of data loaders."""

    def __init__(self):
        # Single Resources
        self.ability = SingleLoader(Ability)
        self.abilitychange = SingleLoader(AbilityChange)
        self.abilitychangeeffect = SingleLoader(AbilityChangeEffectText)
        self.abilityeffect = SingleLoader(AbilityEffectText)
        self.abilityflavortext = SingleLoader(AbilityFlavorText)
        self.abilityname = SingleLoader(AbilityName)
        self.berryfirmness = SingleLoader(BerryFirmness)
        self.berryfirmnessname = SingleLoader(BerryFirmnessName)
        self.berryflavor = SingleLoader(BerryFlavor)
        self.berryflavorname = SingleLoader(BerryFlavorName)
        self.characteristic = SingleLoader(Characteristic)
        self.characteristicdescription = SingleLoader(CharacteristicDescription)
        self.contesteffect = SingleLoader(ContestEffect)
        self.contesteffecteffect = SingleLoader(ContestEffectEffectText)
        self.contesteffectflavortext = SingleLoader(ContestEffectFlavorText)
        self.contesttype = SingleLoader(ContestType)
        self.contesttypename = SingleLoader(ContestTypeName)
        self.egggroup = SingleLoader(EggGroup)
        self.egggroupname = SingleLoader(EggGroupName)
        self.encounter = SingleLoader(Encounter)
        self.encountercondition = SingleLoader(EncounterCondition)
        self.encounterconditionname = SingleLoader(EncounterConditionName)
        self.encounterconditionvalue = SingleLoader(EncounterConditionValue)
        self.encounterconditionvaluename = SingleLoader(EncounterConditionValueName)
        self.encountermethod = SingleLoader(EncounterMethod)
        self.encountermethodname = SingleLoader(EncounterMethodName)
        self.evolutionchain = SingleLoader(EvolutionChain)
        self.evolutiontrigger = SingleLoader(EvolutionTrigger)
        self.evolutiontriggername = SingleLoader(EvolutionTriggerName)
        self.gender = SingleLoader(Gender)
        self.generation = SingleLoader(Generation)
        self.generationname = SingleLoader(GenerationName)
        self.growthrate = SingleLoader(GrowthRate)
        self.growthratedescription = SingleLoader(GrowthRateDescription)
        self.experience = SingleLoader(Experience)
        self.language = SingleLoader(Language)
        self.languagename = SingleLoader(LanguageName)
        self.location = SingleLoader(Location)
        self.locationname = SingleLoader(LocationName)
        self.locationarea = SingleLoader(LocationArea)
        self.locationareaencounterrate = SingleLoader(LocationAreaEncounterRate)
        self.locationareaname = SingleLoader(LocationAreaName)
        self.locationgameindex = SingleLoader(LocationGameIndex)
        self.item = ItemLoader()
        self.itemattribute = SingleLoader(ItemAttribute)
        self.itemattributename = SingleLoader(ItemAttributeName)
        self.itemattributedescription = SingleLoader(ItemAttributeDescription)
        self.itemcategory = SingleLoader(ItemCategory)
        self.itemcategoryname = SingleLoader(ItemCategoryName)
        self.itemeffect = SingleLoader(ItemEffectText)
        self.itemflavortext = SingleLoader(ItemFlavorText)
        self.itemflingeffect = SingleLoader(ItemFlingEffect)
        self.itemflingeffecteffecttext = SingleLoader(ItemFlingEffectEffectText)
        self.itemgameindex = SingleLoader(ItemGameIndex)
        self.itemname = SingleLoader(ItemName)
        self.itempocket = SingleLoader(ItemPocket)
        self.itempocketname = SingleLoader(ItemPocketName)
        self.machine = SingleLoader(Machine)
        self.move = SingleLoader(Move)
        self.movechange = SingleLoader(MoveChange)
        self.moveeffectchange = SingleLoader(MoveEffectChange)
        self.moveeffectchangeeffecttext = SingleLoader(MoveEffectChangeEffectText)
        self.moveeffecteffecttext = SingleLoader(MoveEffectEffectText)
        self.moveflavortext = SingleLoader(MoveFlavorText)
        self.movemeta = SingleLoader(MoveMeta)
        self.movename = SingleLoader(MoveName)
        self.movebattlestylename = SingleLoader(MoveBattleStyleName)
        self.movebattlestyle = SingleLoader(MoveBattleStyle)
        self.movedamageclass = SingleLoader(MoveDamageClass)
        self.movedamageclassname = SingleLoader(MoveDamageClassName)
        self.movedamageclassdescription = SingleLoader(MoveDamageClassDescription)
        self.movelearnmethod = SingleLoader(MoveLearnMethod)
        self.movelearnmethodname = SingleLoader(MoveLearnMethodName)
        self.movelearnmethoddescription = SingleLoader(MoveLearnMethodDescription)
        self.movemetaailment = SingleLoader(MoveMetaAilment)
        self.movemetaailmentname = SingleLoader(MoveMetaAilmentName)
        self.movemetacategory = SingleLoader(MoveMetaCategory)
        self.movemetacategorydescription = SingleLoader(MoveMetaCategoryDescription)
        self.movemetastatchange = SingleLoader(MoveMetaStatChange)
        self.movetarget = SingleLoader(MoveTarget)
        self.movetargetname = SingleLoader(MoveTargetName)
        self.movetargetdescription = SingleLoader(MoveTargetDescription)
        self.nature = SingleLoader(Nature)
        self.naturename = SingleLoader(NatureName)
        self.naturepokeathlonstat = SingleLoader(NaturePokeathlonStat)
        self.naturebattlestylepreference = SingleLoader(NatureBattleStylePreference)
        self.region = SingleLoader(Region)
        self.regionname = SingleLoader(RegionName)
        self.pokedex = SingleLoader(Pokedex)
        self.pokedexdescription = SingleLoader(PokedexDescription)
        self.pokedexname = SingleLoader(PokedexName)
        self.palpark = SingleLoader(PalPark)
        self.palparkarea = SingleLoader(PalParkArea)
        self.palparkareaname = SingleLoader(PalParkAreaName)
        self.pokeathlonstat = SingleLoader(PokeathlonStat)
        self.pokeathlonstatname = SingleLoader(PokeathlonStatName)
        self.pokemon = SingleLoader(Pokemon)
        self.pokemonability = SingleLoader(PokemonAbility)
        self.pokemoncolor = SingleLoader(PokemonColor)
        self.pokemoncolorname = SingleLoader(PokemonColorName)
        self.pokemondexnumber = SingleLoader(PokemonDexNumber)
        self.pokemonevolution = SingleLoader(PokemonEvolution)
        self.pokemonform = SingleLoader(PokemonForm)
        self.pokemonformname = SingleLoader(PokemonFormName)
        self.pokemonformsprites = SingleLoader(PokemonFormSprites)
        self.pokemongameindex = SingleLoader(PokemonGameIndex)
        self.pokemonhabitat = SingleLoader(PokemonHabitat)
        self.pokemonhabitatname = SingleLoader(PokemonHabitatName)
        self.pokemonitem = SingleLoader(PokemonItem)
        self.pokemonmove = SingleLoader(PokemonMove)
        self.pokemonshape = SingleLoader(PokemonShape)
        self.pokemonshapename = SingleLoader(PokemonShapeName)
        self.pokemonspecies = SingleLoader(PokemonSpecies)
        self.pokemonspeciesdescription = SingleLoader(PokemonSpeciesDescription)
        self.pokemonspeciesflavortext = SingleLoader(PokemonSpeciesFlavorText)
        self.pokemonspeciesname = SingleLoader(PokemonSpeciesName)
        self.pokemonsprites = SingleLoader(PokemonSprites)
        self.pokemonstat = SingleLoader(PokemonStat)
        self.pokemontype = SingleLoader(PokemonType)
        self.stat = SingleLoader(Stat)
        self.statname = SingleLoader(StatName)
        self.supercontesteffect = SingleLoader(SuperContestEffect)
        self.supercontesteffectflavortext = SingleLoader(SuperContestEffectFlavorText)
        self.type = SingleLoader(Type)
        self.typegameindex = SingleLoader(TypeGameIndex)
        self.typename = SingleLoader(TypeName)
        self.version = SingleLoader(Version)
        self.versionname = SingleLoader(VersionName)
        self.versiongroup = SingleLoader(VersionGroup)

        # Lists of Sub-Resources (Names, Descriptions, etc.) for a Resource
        self.ability_changes = ListLoader(AbilityChange, "ability_id")
        self.ability_effectentries = TranslationsLoader(AbilityEffectText, "ability_id")
        self.ability_flavortextentries = TranslationsLoader(
            AbilityFlavorText, "ability_id"
        )
        self.ability_names = TranslationsLoader(AbilityName, "ability_id")
        self.abilitychange_effectentries = TranslationsLoader(
            AbilityChangeEffectText, "ability_change_id"
        )
        self.berry_flavormaps = ListLoader(BerryFlavorMap, "berry_id")
        self.berryfirmness_items = BerryFirmnessItemsLoader()
        self.berryfirmness_names = TranslationsLoader(
            BerryFirmnessName, "berry_firmness_id"
        )
        self.berryflavor_names = TranslationsLoader(BerryFlavorName, "berry_flavor_id")
        self.berryflavor_maps = ListLoader(BerryFlavorMap, "berry_flavor_id")
        self.characteristic_descriptions = TranslationsLoader(
            CharacteristicDescription, "characteristic_id"
        )
        self.contesteffect_effectentries = TranslationsLoader(
            ContestEffectEffectText, "contest_effect_id"
        )
        self.contesteffect_flavortextentries = TranslationsLoader(
            ContestEffectFlavorText, "contest_effect_id"
        )
        self.contesttype_names = TranslationsLoader(ContestTypeName, "contest_type_id")
        self.egggroup_names = TranslationsLoader(EggGroupName, "egg_group_id")
        self.encountercondition_names = TranslationsLoader(
            EncounterConditionName, "encounter_condition_id"
        )
        self.encountercondition_values = ListLoader(
            EncounterConditionValue, "encounter_condition_id"
        )
        self.encounterconditionvalue_names = TranslationsLoader(EncounterConditionValueName, "encounter_condition_value_id")
        self.encountermethod_names = TranslationsLoader(EncounterMethodName, "encounter_method_id")
        self.evolutionchain_pokemonspecies = EvolutionChainPokemonSpeciesLoader()
        self.evolutiontrigger_names = TranslationsLoader(EvolutionTriggerName, "evolution_trigger_id")
        self.growthrate_descriptions = TranslationsLoader(GrowthRateDescription, "growth_rate_id")
        self.growthrate_experiences = ListLoader(Experience, "growth_rate_id")
        self.generation_names = TranslationsLoader(GenerationName, "generation_id")
        self.itemattribute_descriptions = TranslationsLoader(ItemAttributeDescription, "item_attribute_id")
        self.itemattribute_names = TranslationsLoader(ItemAttributeName, "item_attribute_id")
        self.item_attributes = ItemAttributesLoader()
        self.item_effectentries = TranslationsLoader(ItemEffectText, "item_id")
        self.item_flavortextentries = TranslationsLoader(ItemFlavorText, "item_id")
        self.item_gameindices = ListLoader(ItemGameIndex, "item_id")
        self.item_names = TranslationsLoader(ItemName, "item_id")
        self.item_machines = ListLoader(Machine, "item_id")
        self.item_sprites = ItemSpritesLoader()
        self.itemcategory_names = TranslationsLoader(ItemCategoryName, "item_category_id")
        self.itemflingeffect_effectentries = TranslationsLoader(ItemFlingEffectEffectText, "item_fling_effect_id")
        self.itemflingeffect_items = ListLoader(Item, "item_fling_effect_id")
        self.itempocket_categories = ListLoader(ItemCategory, "item_pocket_id")
        self.itempocket_names = TranslationsLoader(ItemPocketName, "item_pocket_id")
        self.language_names = LanguageNamesLoader()
        self.location_gameindices = ListLoader(LocationGameIndex, "location_id")
        self.location_names = TranslationsLoader(LocationName, "location_id")
        self.locationarea_names = TranslationsLoader(LocationAreaName, "location_area_id")
        self.move_changes = ListLoader(MoveChange, "move_id")
        self.move_contestcombos = ContestCombosByMoveLoader(ContestCombo)
        self.move_supercontestcombos = ContestCombosByMoveLoader(SuperContestCombo)
        self.move_effectchanges = ListLoader(MoveEffectChange, "move_effect_id")
        self.move_flavortextentries = TranslationsLoader(MoveFlavorText, "move_id")
        self.move_machines = ListLoader(Machine, "move_id")
        self.move_names = TranslationsLoader(MoveName, "move_id")
        self.move_statchanges = ListLoader(MoveMetaStatChange, "move_id")
        self.moveeffect_effectentries = TranslationsLoader(
            MoveEffectEffectText, "move_effect_id"
        )
        self.moveeffectchange_effectentries = TranslationsLoader(
            MoveEffectChangeEffectText, "move_effect_change_id"
        )
        self.movebattlestyle_names = TranslationsLoader(
            MoveBattleStyleName, "move_battle_style_id"
        )
        self.movedamageclass_names = TranslationsLoader(
            MoveDamageClassName, "move_damage_class_id"
        )
        self.movedamageclass_descriptions = TranslationsLoader(
            MoveDamageClassDescription, "move_damage_class_id"
        )
        self.movelearnmethod_names = TranslationsLoader(
            MoveLearnMethodName, "move_learn_method_id"
        )
        self.movelearnmethod_descriptions = TranslationsLoader(
            MoveLearnMethodDescription, "move_learn_method_id"
        )
        self.movemetacategory_descriptions = TranslationsLoader(
            MoveMetaCategoryDescription, "move_meta_category_id"
        )
        self.movemetaailment_names = TranslationsLoader(
            MoveMetaAilmentName, "move_meta_ailment_id"
        )
        self.movetarget_names = TranslationsLoader(MoveTargetName, "move_target_id")
        self.movetarget_descriptions = TranslationsLoader(
            MoveTargetDescription, "move_target_id"
        )
        self.nature_names = TranslationsLoader(NatureName, "nature_id")
        self.nature_statchanges = ListLoader(NaturePokeathlonStat, "nature_id")
        self.nature_battlestylepreferences = ListLoader(
            NatureBattleStylePreference, "nature_id"
        )
        self.region_names = TranslationsLoader(RegionName, "region_id")
        self.palparkarea_names = TranslationsLoader(PalParkAreaName, "pal_park_area_id")
        self.pokeathlonstat_names = TranslationsLoader(PokeathlonStatName, "pokeathlon_stat_id")
        self.pokedex_descriptions = TranslationsLoader(PokedexDescription, "pokedex_id")
        self.pokedex_names = TranslationsLoader(PokedexName, "pokedex_id")
        self.pokemon_abilities = ListLoader(PokemonAbility, "pokemon_id")
        self.pokemon_forms = ListLoader(PokemonForm, "pokemon_id")
        self.pokemon_gameindices = ListLoader(PokemonGameIndex, "pokemon_id")
        self.pokemon_items = ListLoader(PokemonItem, "pokemon_id")
        self.pokemon_sprites = PokemonSpritesLoader()
        self.pokemon_stats = ListLoader(PokemonStat, "pokemon_id")
        self.pokemon_types = ListLoader(PokemonType, "pokemon_id")
        self.pokemoncolor_names = TranslationsLoader(PokemonColorName, "pokemon_color_id")
        self.pokemonform_names = TranslationsLoader(PokemonFormName, "pokemon_form_id")
        self.pokemonform_sprites = PokemonFormSpritesLoader()
        self.pokemonhabitat_names = TranslationsLoader(
            PokemonHabitatName, "pokemon_habitat_id"
        )
        self.pokemonshape_names = TranslationsLoader(PokemonShapeName, "pokemon_shape_id")
        self.pokemonspecies_descriptions = TranslationsLoader(
            PokemonSpeciesDescription, "pokemon_species_id"
        )
        self.pokemonspecies_flavortextentries = TranslationsLoader(
            PokemonSpeciesFlavorText, "pokemon_species_id"
        )
        self.pokemonspecies_names = TranslationsLoader(
            PokemonSpeciesName, "pokemon_species_id"
        )
        self.pokemonspecies_dexnumbers = ListLoader(PokemonDexNumber, "pokemon_species_id")
        self.supercontesteffect_flavortextentries = TranslationsLoader(
            SuperContestEffectFlavorText, "super_contest_effect_id"
        )
        self.supercontesteffect_moves = ListLoader(Move, "super_contest_effect_id")
        self.stat_names = TranslationsLoader(StatName, "stat_id")
        self.type_gameindices = ListLoader(TypeGameIndex, "type_id")
        self.type_names = TranslationsLoader(TypeName, "type_id")
        self.version_names = TranslationsLoader(VersionName, "version_id")

        # Lists of Resources by other resources
        self.characteristics_by_stat = ListLoader(Characteristic, "stat_id")
        self.encounters_by_locationarea_and_pokemon = EncountersByLocationAreaAndPokemonLoader()
        self.egggroups_by_pokemonspecies = EggGroupsByPokemonSpeciesLoader()
        self.encounterconditionvalues_by_encounter = EncounterConditionValuesByEncounterLoader()
        self.locationareas_by_location = ListLoader(LocationArea, "location_id")
        self.locationareaencounterrates_by_locationarea = ListLoader(
            LocationAreaEncounterRate, "location_area_id"
        )
        self.natures_by_decreasedstat = ListLoader(Nature, "decreased_stat_id")
        self.natures_by_increasedstat = ListLoader(Nature, "increased_stat_id")
        self.palparks_by_pokemonspecies = ListLoader(PalPark, "pokemon_species_id")
        self.pokedexes_by_region = ListLoader(Pokedex, "region_id")
        self.pokemon_by_pokemonspecies = ListLoader(Pokemon, "pokemon_species_id")
        self.pokemonevolutions_by_pokemonspecies = ListLoader(
            PokemonEvolution, "evolved_species_id"
        )
        self.pokemonitems_by_item_and_pokemon = PokemonItemsByItemAndPokemonLoader()
        self.pokemonmove_by_move_and_pokemon = PokemonMovesByMoveAndPokemonLoader()
        self.typeefficacies_by_damagetype = TypeEfficaciesByDamageTypeLoader()
        self.typeefficacies_by_targettype = TypeEfficaciesByTargetTypeLoader()
        self.types_by_generation = ListLoader(Type, "generation_id")
        self.versions_by_versiongroup = ListLoader(Version, "version_group_id")
        self.versiongroups_by_generation = ListLoader(VersionGroup, "generation_id")
        self.versiongroups_by_movelearnmethod = VersionGroupsByMoveLearnMethodLoader()
        self.versiongroups_by_region = VersionGroupsByRegionLoader()

        # Single Resources by other resources
        self.berryflavor_by_contesttype = BerryFlavorByContestTypeLoader()
        self.evolutionchain_by_item = EvolutionChainByItemLoader()
        self.generation_by_region = GenerationByRegionLoader()
        self.growthrateexperience_by_level = GrowthRateExperienceByLevelLoader()
        self.item_by_berry = ItemByBerryLoader()
        self.movemeta_by_move = MoveMetaByMoveLoader()

        # Single Resources with other resources
        self.berry_with_item = BerryWithItemLoader()
        self.encounter_with_encounterslot = EncounterWithEncounterSlotLoader()


# Abstract Loaders
#######################################
class SingleLoader(DataLoader):
    def __init__(self, model):
        super(SingleLoader, self).__init__()
        self.model = model

    def batch_load_fn(self, keys):
        q = self.model.objects.filter(id__in=keys)
        results = divide_by_key(keys, q, lambda key, obj: str(obj.id) == str(key))
        return Promise.resolve(results)


class ListLoader(DataLoader):
    def __init__(self, model, id_attr):
        super(ListLoader, self).__init__()
        self.model = model
        self.id_attr = id_attr

    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, self.id_attr)
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return self.model.objects.filter(**{self.id_attr + "__in": ids})


class TranslationsLoader(DataLoader):
    def __init__(self, model, id_attr):
        super(TranslationsLoader, self).__init__()
        self.model = model
        self.id_attr = id_attr

    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, self.id_attr)
        sorted_results = []
        for (i, result) in enumerate(results):

            # Sort results based on the order in the 'lang' argument, if present
            def sort_results(translation):
                args = keys[i].args._asdict()
                if 'lang' in args:
                    return args["lang"].index(translation.language.name)
                return translation.id

            sorted_results.append(sorted(result, key=sort_results))

        return Promise.resolve(sorted_results)

    def get_query_set(self, ids, **args):
        q = self.model.objects.filter(**{self.id_attr + "__in": ids})
        q = q.select_related('language')
        q = add_filters(q, args, language__name__in="lang")
        return q


# Single Resources
#######################################
class ItemLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Item.objects.filter(id__in=keys)
        q = q.prefetch_related("berry")
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.id) == str(key)
        )
        return Promise.resolve(results)


# Lists of Resources
#############################################

class BerryFirmnessItemsLoader(DataLoader):
    def batch_load_fn(self, keys):
        data = get_relations(keys, self.get_query_set, "berry_firmness_id")
        results = [[result.item for result in d] for d in data]
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = Berry.objects.filter(berry_firmness_id__in=ids)
        q = q.select_related("item")
        return q


class EvolutionChainPokemonSpeciesLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "evolution_chain_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = PokemonSpecies.objects.filter(evolution_chain_id__in=ids).order_by("order")
        return q


class ItemAttributesLoader(DataLoader):
    def batch_load_fn(self, keys):
        data = get_relations(keys, self.get_query_set, "item_id")
        results = [[result.item_attribute for result in d] for d in data]
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = ItemAttributeMap.objects.filter(item_id__in=ids)
        q = q.select_related("item_attribute")
        return q


class ItemSpritesLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = ItemSprites.objects.filter(item_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.item_id) == str(key)
        )
        return Promise.resolve(results)


class LanguageNamesLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "language_id")

        sorted_results = []
        for (i, result) in enumerate(results):

            # Sort results based on the order in the 'lang' argument, if present
            def sort_results(lang_name):
                args = keys[i].args._asdict()
                if 'lang' in args:
                    return args["lang"].index(lang_name.local_language.name)
                return lang_name.id

            sorted_results.append(sorted(result, key=sort_results))

        return Promise.resolve(sorted_results)

    def get_query_set(self, ids, **args):
        q = LanguageName.objects.filter(language_id__in=ids)
        q = q.select_related('local_language')
        q = add_filters(q, args, local_language__name__in="lang")
        return q


class PokemonFormSpritesLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = PokemonFormSprites.objects.filter(pokemon_form_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.pokemon_form_id) == str(key)
        )
        return Promise.resolve(results)


class PokemonSpritesLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = PokemonSprites.objects.filter(pokemon_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.pokemon_id) == str(key)
        )
        return Promise.resolve(results)


# Lists of Resources by other resources
########################################################
class ContestCombosByMoveLoader(DataLoader):
    def __init__(self, model):
        super(ContestCombosByMoveLoader, self).__init__()
        self.model = model

    def batch_load_fn(self, keys):
        all_combos = self.model.objects.filter(
            Q(first_move_id__in=keys) | Q(second_move_id__in=keys)
        ).select_related('first_move', 'second_move')

        results = [
            [combo for combo in all_combos
                if key == combo.first_move_id or key == combo.second_move_id
            ] for key in keys
        ]

        return Promise.resolve(results)


class EncountersByLocationAreaAndPokemonLoader(DataLoader):
    def batch_load_fn(self, keys):
        pokemon_ids = [key.args.pokemon_id for key in keys]
        location_area_ids = [key.args.location_area_id for key in keys]
        all_encounters = Encounter.objects.filter(
            location_area_id__in=location_area_ids, pokemon_id__in=pokemon_ids
        ).select_related('encounter_slot')

        results = [
            [e for e in all_encounters
                if e.pokemon_id == key.args.pokemon_id
                and e.location_area_id == key.args.location_area_id
            ] for key in keys
        ]

        return Promise.resolve(results)


class EncounterConditionValuesByEncounterLoader(DataLoader):
    def batch_load_fn(self, keys):
        data = get_relations(keys, self.get_query_set, "encounter_id")
        results = [[result.encounter_condition_value for result in d] for d in data]
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = EncounterConditionValueMap.objects.filter(encounter_id__in=ids)
        q = q.select_related("encounter_condition_value")
        return q


class EggGroupsByPokemonSpeciesLoader(DataLoader):
    def batch_load_fn(self, keys):
        data = get_relations(keys, self.get_query_set, "pokemon_species_id")
        results = [[result.egg_group for result in d] for d in data]
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = PokemonEggGroup.objects.filter(pokemon_species_id__in=ids)
        q = q.select_related("egg_group")
        return q


class PokemonItemsByItemAndPokemonLoader(DataLoader):
    def batch_load_fn(self, keys):
        pokemon_ids = [key.args.pokemon_id for key in keys]
        item_ids = [key.args.item_id for key in keys]

        pokemon_items = PokemonItem.objects.filter(
            item_id__in=item_ids, pokemon_id__in=pokemon_ids
        )

        # Split up
        results = [
            [pi for pi in pokemon_items
                if pi.pokemon_id == key.args.pokemon_id
                and pi.item_id == key.args.item_id
            ] for key in keys
        ]

        return Promise.resolve(results)


class PokemonMovesByMoveAndPokemonLoader(DataLoader):
    def batch_load_fn(self, keys):
        pokemon_ids = [key.args.pokemon_id for key in keys]
        move_ids = [key.args.move_id for key in keys]

        all_pokemon_moves = PokemonMove.objects.filter(
            move_id__in=move_ids, pokemon_id__in=pokemon_ids
        )

        # Split up
        results = [
            [pm for pm in all_pokemon_moves
                if pm.pokemon_id == key.args.pokemon_id
                and pm.move_id == key.args.move_id
            ] for key in keys
        ]

        return Promise.resolve(results)


class TypeEfficaciesByDamageTypeLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "damage_type_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = TypeEfficacy.objects.filter(damage_type_id__in=ids)
        q = q.select_related("target_type")
        return q


class TypeEfficaciesByTargetTypeLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "target_type_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = TypeEfficacy.objects.filter(target_type_id__in=ids)
        q = q.select_related("damage_type")
        return q


class VersionGroupsByMoveLearnMethodLoader(DataLoader):
    def batch_load_fn(self, keys):
        data = get_relations(keys, self.get_query_set, "move_learn_method_id")
        results = [[result.version_group for result in d] for d in data]
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q =  VersionGroupMoveLearnMethod.objects.filter(move_learn_method_id__in=ids)
        q = q.select_related("version_group")
        return q


class VersionGroupsByRegionLoader(DataLoader):
    def batch_load_fn(self, keys):
        data = get_relations(keys, self.get_query_set, "region_id")
        results = [[result.version_group for result in d] for d in data]
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = VersionGroupRegion.objects.filter(region_id__in=ids)
        q = q.select_related("version_group")
        return q


# Single Resources by other resources
######################################################
class BerryFlavorByContestTypeLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = BerryFlavor.objects.filter(contest_type_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.contest_type_id) == str(key)
        )
        return Promise.resolve(results)


class EvolutionChainByItemLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = EvolutionChain.objects.filter(baby_trigger_item_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.baby_trigger_item_id) == str(key)
        )
        return Promise.resolve(results)


class GenerationByRegionLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Generation.objects.filter(region_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.region_id) == str(key)
        )
        return Promise.resolve(results)


class GrowthRateExperienceByLevelLoader(DataLoader):
    def batch_load_fn(self, keys):
        levels = [key.args.level for key in keys]
        ids = [key.id for key in keys]
        q = Experience.objects.filter(growth_rate_id__in=ids)
        q = q.filter(level__in=levels)
        results = divide_by_key(
            keys, q,
            lambda key, obj: (
                str(obj.growth_rate_id) == str(key.id)
                and str(obj.level) == str(key.args.level)
            )
        )
        return Promise.resolve(results)


class ItemByBerryLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Item.objects.filter(berry__id__in=keys).prefetch_related("berry")
        results = divide_by_key(keys, q, self.compare_keys)
        return Promise.resolve(results)

    def compare_keys(self, key, item):
        berries = list(item.berry.all())
        if len(berries) == 1:
            berry = berries[0]
            return str(berry.id) == str(key)
        return False


class MoveMetaByMoveLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = MoveMeta.objects.filter(move_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.move_id) == str(key)
        )
        return Promise.resolve(results)


# Single Resources with other resources
######################################################
class BerryWithItemLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Berry.objects.filter(id__in=keys)
        q = q.select_related("item")
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.id) == str(key)
        )
        return Promise.resolve(results)


class EncounterWithEncounterSlotLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Encounter.objects.filter(id__in=keys)
        q = q.select_related("encounter_slot")
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.id) == str(key)
        )
        return Promise.resolve(results)
