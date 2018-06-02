from promise import Promise
from promise.dataloader import DataLoader
from django.db.models import Q

from pokemon_v2.models import *
from .loader_util import (
    divide_by_key,
    get_relations,
    get_relations_via_map,
    add_filters,
)

"""
Data loaders batch and cache requests to the database. Each request gets a new instance
of Loaders, so caching is per-request only (see middleware for the specifics). Each data
loader returns a list of Django model objects. Any manipulation occurs elsewhere in the
program (schema, etc.).

To use a data loader, instantiate a Loaders object (or get it from the context), then
call the `load()` method on a specific loader, passing in a key. Data loaders take one
of two kinds of keys: simple integer IDs, or instances of LoaderKey. Loaders that return
simple objects take integer IDs, while loaders that return lists of objects take
LoaderKey instances, allowing for complex filtering, etc. The loader will return a
Promise.

For more information about DataLoader, see https://github.com/syrusakbary/aiodataloader.
"""

class Loaders(object):
    """Create a new set of data loaders."""
    def __init__(self):
        # Single Resources
        self.encounter = SingleLoader(Encounter)
        self.encountermethod = SingleLoader(EncounterMethod)
        self.generation = SingleLoader(Generation)
        self.language = SingleLoader(Language)
        self.location = SingleLoader(Location)
        self.locationarea = SingleLoader(LocationArea)
        self.locationareaencounterrate = SingleLoader(LocationAreaEncounterRate)
        self.locationgameindex = SingleLoader(LocationGameIndex)
        self.region = SingleLoader(Region)
        self.version = SingleLoader(Version)
        self.versiongroup = SingleLoader(VersionGroup)

        # Single Resource Names, Descriptions, etc.
        self.encountermethodname = SingleLoader(EncounterMethodName)
        self.languagename = SingleLoader(LanguageName)
        self.locationname = SingleLoader(LocationName)
        self.locationareaname = SingleLoader(LocationAreaName)
        self.generationname = SingleLoader(GenerationName)
        self.regionname = SingleLoader(RegionName)
        self.versionname = SingleLoader(VersionName)

        # Lists of Resource Names, Descriptions, etc.
        self.encountermethod_names = NamesLoader(EncounterMethodName, "encounter_method_id")
        self.generation_names = NamesLoader(GenerationName, "generation_id")
        self.language_names = NamesLoader(LanguageName, "language_id")
        self.location_gameindices = LocationGameIndicesLoader()
        self.location_names = NamesLoader(LocationName, "location_id")
        self.locationarea_names = NamesLoader(LocationAreaName, "location_area_id")
        self.region_names = NamesLoader(RegionName, "region_id")
        self.version_names = NamesLoader(VersionName, "version_id")

        # Lists of Resources by other resources (sorted by "By")
        self.encounterconditionvalues_by_encounter = EncounterConditionValuesByEncounterLoader()
        self.versiongroups_by_generation = VersionGroupsByGenerationLoader()
        self.types_by_generation = TypesByGenerationLoader()
        self.locationareaencounterrates_by_locationarea = LocationAreaEncounterRatesByLocationAreaLoader()
        self.pokedexes_by_region = PokedexesByRegionLoader()
        self.versiongroups_by_region = VersionGroupsByRegionLoader()
        self.versions_by_versiongroup = VersionsByVersionGroupLoader()
        self.locationareas_by_location = VersionsByVersionGroupLoader()

        # Single Resources by other resources (sorted by "By")
        self.generation_by_region = GenerationByRegionLoader()

        # Single Resources With other resource(s)
        self.encounter_with_encounterslot = EncounterWithEncounterSlotLoader()


#######################################
class SingleLoader(DataLoader):
    def __init__(self, model):
        super(SingleLoader, self).__init__()
        self.model = model

    def batch_load_fn(self, keys):
        q = self.model.objects.filter(id__in=keys)
        results = divide_by_key(keys, q, lambda key, obj: str(obj.id) == str(key))
        return Promise.resolve(results)


class NamesLoader(DataLoader):
    def __init__(self, model, id_attr):
        super(NamesLoader, self).__init__()
        self.model = model
        self.id_attr = id_attr

    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, self.id_attr)
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = self.model.objects.filter(**{self.id_attr + "__in": ids})
        q = add_filters(q, args, language__name="lang")
        return q


#######################################
class LocationGameIndicesLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, 'location_id')
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q =  LocationGameIndex.objects.filter(location_id__in=ids)
        return q


#######################################
class EncounterConditionValuesByEncounterLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations_via_map(
            keys, self.get_query_set, "encounter_id", "encounterconditionvaluemap"
        )
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = EncounterConditionValue.objects.all()
        q = q.filter(encounterconditionvaluemap__encounter_id__in=ids)
        return q


class VersionGroupsByGenerationLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "generation_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return VersionGroup.objects.filter(generation_id__in=ids)


class TypesByGenerationLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "generation_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return Type.objects.filter(generation_id__in=ids)


class LocationAreaEncounterRatesByLocationAreaLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "location_area_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return LocationAreaEncounterRate.objects.filter(location_area_id__in=ids)


class VersionsByVersionGroupLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "version_group_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return Version.objects.filter(version_group_id__in=ids)


class LocationAreasByLocationLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, 'location_id')
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = LocationArea.objects.filter(location_id__in=ids)
        return q


class PokedexesByRegionLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, 'region_id')
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = Pokedex.objects.filter(region_id__in=ids)
        return q


class VersionGroupsByRegionLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations_via_map(
            keys, self.get_query_set, 'region_id', 'versiongroupregion'
        )
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        q = VersionGroup.objects.all()
        q = q.filter(versiongroupregion__region_id__in=ids)
        return q


#######################################
class GenerationByRegionLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Generation.objects.filter(region_id__in=keys)
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.region_id) == str(key)
        )
        return Promise.resolve(results)


#######################################
class EncounterWithEncounterSlotLoader(DataLoader):
    def batch_load_fn(self, keys):
        q = Encounter.objects.filter(id__in=keys)
        q = q.select_related('encounter_slot')
        results = divide_by_key(
            keys, q, lambda key, obj: str(obj.id) == str(key)
        )
        return Promise.resolve(results)
