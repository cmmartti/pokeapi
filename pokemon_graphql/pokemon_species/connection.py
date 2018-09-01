# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay
from django_subquery.expressions import Subquery, OuterRef

from pokemon_v2 import models
from .types import PokemonSpecies
from ..base import BaseConnection, BaseOrder
from ..where import BaseWhere, TranslationSearch

class PokemonSpeciesConnection(BaseConnection, relay.Connection):
    class Meta:
        node = PokemonSpecies


class PokemonSpeciesOrdering(BaseOrder):
    sort = InputField(
        Enum('PokemonSpeciesSort', [
            ("BASE_HAPPINESS", "base_happiness"),
            ("CAPTURE_RATE", "capture_rate"),
            ("GENDER_RATE", "gender_rate"),
            ("FORMS_SWITCHABLE", "forms_switchable"),
            ("HAS_GENDER_DIFFERENCES", "has_gender_differences"),
            ("HATCH_COUNTER", "hatch_counter"),
            ("IS_BABY", "is_baby"),
            ("ORDER", "order"),
            ("NAME", "name_translation"),
        ]),
        description="The field to sort by."
    )

    @classmethod
    def apply(cls, query_set, order_by):
        for o in order_by:
            if o.sort == "name_translation":
                lang = o.get("lang", None)
                assert lang, "Argument 'lang' **must** be specified for sorts with text translations."
                subquery = models.PokemonSpeciesName.objects.filter(
                    pokemon_species_id=OuterRef("pk"),
                    language__name=lang
                )
                query_set = query_set.annotate(
                    name_translation=Subquery(subquery.values("name")[:1])
                )

        return query_set


class PokemonSpeciesWhere(BaseWhere):
    base_happiness__gt = Int(name="baseHappiness_gt")
    capture_rate__gt = Int(name="captureRate_gt")
    color = ID()
    name = Argument(TranslationSearch)

    @classmethod
    def apply(cls, query_set, **where):

        name = where.pop("name", None)
        if name:
            if name.case_sensitive:
                query_set = query_set.filter(pokemonspeciesname__name__contains=name.query)
            else:
                query_set = query_set.filter(pokemonspeciesname__name__icontains=name.query)

        color = where.pop("color", None)
        if color:
            id = cls.get_id(color, "PokemonColor", "color")
            query_set = query_set.filter(pokemon_color=id)

        return super(PokemonSpeciesWhere, cls).apply(query_set, **where)
