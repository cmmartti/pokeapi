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


class Loaders(object):
    """Create a new set of dataloaders."""
    def __init__(self):
        self.language = SingleLoader(Language)
        self.generation = SingleLoader(Generation)
        self.version = SingleLoader(Version)
        self.versiongroup = SingleLoader(VersionGroup)

        self.languagename = SingleLoader(LanguageName)
        self.generationname = SingleLoader(GenerationName)
        self.versionname = SingleLoader(VersionName)

        self.language_names = NamesLoader(LanguageName, "language_id")
        self.generation_names = NamesLoader(GenerationName, "generation_id")
        self.version_names = NamesLoader(VersionName, "version_id")

        self.versiongroups_by_generation = VersionGroupsByGenerationLoader()
        self.versions_by_versiongroup = VersionsByVersionGroupLoader()


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
class VersionGroupsByGenerationLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "generation_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return VersionGroup.objects.filter(generation_id__in=ids)


class VersionsByVersionGroupLoader(DataLoader):
    def batch_load_fn(self, keys):
        results = get_relations(keys, self.get_query_set, "version_group_id")
        return Promise.resolve(results)

    def get_query_set(self, ids, **args):
        return Version.objects.filter(version_group_id__in=ids)
