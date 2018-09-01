# -*- coding: utf-8 -*-
from graphene import *
from graphene import relay

from ..connections import getConnection, getPage
from ..base import BaseConnection, BaseOrder, BaseName, BaseEffect, BaseVerboseEffect, BaseFlavorText
from ..loader_key import LoaderKey
from ..relay_node import RelayNode
from ..field import TranslationList


class Move(ObjectType):
    """
    Moves are the skills of Pokémon in battle. In battle, a Pokémon uses one move each turn. Some moves (including those learned by Hidden Machine) can be used outside of battle as well, usually for the purpose of removing obstacles or exploring new areas.
    """

    name = String(description="The name of this resource.")
    names = TranslationList(
        lambda: MoveName,
        description="The name of this move listed in different languages.",
        resolver=lambda root, info, **kwargs: \
            info.context.loaders.move_names.load(LoaderKey(root.id, **kwargs))
    )
    accuracy = Int(
        description="The percent value of how likely this move is to be successful."
    )
    contest_combos = Field(
        lambda: ContestComboDetail,
        description="A detail of moves this move can be used before or after, granting additional appeal points in contests.",
        resolver=lambda root, info: \
            info.context.loaders.move_contestcombos.load(root.id).then(
                lambda data: Move.get_combo_details(root, data)
            )
    )
    contest_effect_id = None
    contest_effect = Field(
        lazy_import("pokemon_graphql.contest_effect.types.ContestEffect"),
        description="The effect the move has when used in a contest.",
        resolver=lambda root, info: \
            info.context.loaders.contesteffect.load(root.contest_effect_id)
    )
    contest_type_id = None
    contest_type = Field(
        lazy_import("pokemon_graphql.contest_type.types.ContestType"),
        description="The type of appeal this move gives a Pokémon when used in a contest.",
        resolver=lambda root, info: \
            info.context.loaders.contesttype.load(root.contest_type_id)
    )
    move_damage_class_id = None
    damage_class = Field(
        lazy_import("pokemon_graphql.move_damage_class.types.MoveDamageClass"),        description="The type of damage the move inflicts on the target, e.g. physical.",
        resolver=lambda root, info: \
            info.context.loaders.movedamageclass.load(root.move_damage_class_id)
    )
    move_effect_chance = Int(
        name="effectChance",
        description="The percent value of how likely it is this moves effect will happen."
    )
    effect_changes = List(
        lambda: MoveEffectChange,
        description="The list of previous effects this move has had across version groups of the games.",
        resolver=lambda root, info: \
            info.context.loaders.move_effectchanges.load(
                LoaderKey(root.move_effect_id)
            )
    )
    effect_entries = TranslationList(
        lambda: MoveEffectText,
        description="The effect of this move listed in different languages.",
        resolver=lambda root, info, **kwargs: \
            info.context.loaders.moveeffect_effectentries.load(
                LoaderKey(root.move_effect_id, **kwargs)
            )
    )
    flavor_text_entries = TranslationList(
        lambda: MoveFlavorText,
        description="The flavor text of this move listed in different languages.",
        resolver=lambda root, info, **kwargs: \
            info.context.loaders.move_flavortextentries.load(
                LoaderKey(root.id, **kwargs)
            )
    )
    generation_id = None
    generation = Field(
        lazy_import("pokemon_graphql.generation.types.Generation"),
        description="The generation in which this move was introduced.",
        resolver=lambda root, info: \
            info.context.loaders.generation.load(root.generation_id)
    )
    machines = List(
        lazy_import("pokemon_graphql.machine.types.Machine"),
        description="A list of the machines that teach this move.",
        resolver=lambda root, info: \
            info.context.loaders.move_machines.load(LoaderKey(root.id))
    )
    meta = Field(
        lambda: MoveMeta,
        description="Metadata about this move.",
        resolver=lambda root, info: info.context.loaders.movemeta_by_move.load(root.id)
    )
    move_effect_id = None
    past_values = List(
        lambda: MoveChange,
        description="A list of move resource value changes across version groups of the game",
        resolver=lambda root, info: \
            info.context.loaders.move_changes.load(LoaderKey(root.id))
    )
    pp = Int(description="Power points. The number of times this move can be used.")
    priority = Int(
        description="A value between -8 and 8. Sets the order in which moves are executed during battle. See [Bulbapedia](http://bulbapedia.bulbagarden.net/wiki/Priority) for greater detail."
    )
    power = Int(
        description="The base power of this move with a value of 0 if it does not have a base power."
    )
    stat_changes = List(
        lambda: MoveStatChange,
        description=".A list of stats this moves effects and how much it effects them",
        resolver=lambda root, info: \
            info.context.loaders.move_statchanges.load(LoaderKey(root.id)).then(
                lambda data: [MoveStatChange.fill(stat_change) for stat_change in data]
            )
    )
    super_contest_combos = Field(
        lambda: ContestComboDetail,
        description="A detail of moves this move can be used before or after, granting additional appeal points in super contests.",
        resolver=lambda root, info: \
            info.context.loaders.move_supercontestcombos.load(root.id).then(
                lambda data: Move.get_combo_details(root, data)
            )
    )
    super_contest_effect_id = None
    super_contest_effect = Field(
        lazy_import("pokemon_graphql.super_contest_effect.types.SuperContestEffect"),        description="The effect the move has when used in a super contest.",
        resolver=lambda root, info: \
            info.context.loaders.supercontesteffect.load(root.super_contest_effect_id)
    )
    move_target_id = None
    target = Field(
        lazy_import("pokemon_graphql.move_target.types.MoveTarget"),
        description="The type of target that will receive the effects of the attack.",
        resolver=lambda root, info: \
            info.context.loaders.movetarget.load(root.move_target_id)
    )
    type_id = None
    type = Field(
        lazy_import("pokemon_graphql.type.types.Type"),
        description="The elemental type of this move.",
        resolver=lambda root, info: info.context.loaders.type.load(root.type_id)
    )

    @staticmethod
    def get_combo_details(root, combos):
        use_before = []
        use_after = []
        for combo in combos:
            if root.id == combo.first_move_id:
                use_before.append(combo.second_move)
            if root.id == combo.second_move_id:
                use_after.append(combo.first_move)
        return ContestComboDetail(use_before=use_before, use_after=use_after)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.move.load(id)


class MoveConnection(BaseConnection, relay.Connection):
    class Meta:
        node = Move


class MoveOrdering(BaseOrder):
    sort = InputField(
        Enum('MoveSort', [
            ("ACCURACY", "accuracy"),
            ("EFFECT_CHANCE", "move_effect_chance"),
            ("PP", "pp"),
            ("PRIORITY", "priority"),
            ("POWER", "power"),
            ("META_AILMENT_CHANCE", "movemeta__ailment_chance"),
            ("META_CRIT_RATE", "movemeta__crit_rate"),
            ("META_DRAIN", "movemeta__drain"),
            ("META_FLINCH_CHANCE", "movemeta__flinch_chance"),
            ("META_HEALING", "movemeta__healing"),
            ("META_MIN_HITS", "movemeta__min_hits"),
            ("META_MAX_HITS", "movemeta__max_hits"),
            ("META_MIN_TURNS", "movemeta__min_turns"),
            ("META_MAX_TURNS", "movemeta__max_turns"),
            ("META_STAT_CHANCE", "movemeta__stat_chance"),
            ("NAME", "name"),
        ]),
        description="The field to sort by."
    )


class MoveName(BaseName):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movename.load(id)


class ContestComboDetail(ObjectType):
    use_before = List(
        lazy_import("pokemon_graphql.move.types.Move"),
        description="A list of moves to use before this move.",
    )
    use_after = List(
        lazy_import("pokemon_graphql.move.types.Move"),
        description="A list of moves to use after this move.",
    )


class MoveFlavorText(BaseFlavorText):
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        resolver=lambda root, info: \
            info.context.loaders.versiongroup.load(root.version_group_id)
    )
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.moveflavortext.load(id)


class MoveEffectText(BaseVerboseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.moveeffecteffecttext.load(id).then(cls.fill)

    @staticmethod
    def fill(data):
        obj = MoveEffectText(
            id=data.id,
            effect=data.effect,
            short_effect=data.short_effect
        )
        obj.language_id = data.language_id
        return obj


class MoveEffectChange(ObjectType):
    effect_entries = TranslationList(
        lambda: MoveEffectChangeEffectText,
        description="The list of previous effects this move has had across version groups of the games."
    )
    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group in which the previous effect of this ability originated.",
        resolver=lambda root, info: \
            info.context.loaders.versiongroup.load(root.version_group_id)
    )

    def resolve_effect_entries(self, info, **kwargs):
        key = LoaderKey(self.id, **kwargs)
        return info.context.loaders.moveeffectchange_effectentries.load(key)

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.moveeffectchange.load(id)


class MoveEffectChangeEffectText(BaseEffect):
    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.moveeffectchangeeffecttext.load(id)


class MoveMeta(ObjectType):
    move_meta_ailment_id = None
    ailment = Field(
        lazy_import("pokemon_graphql.move_ailment.types.MoveAilment"),
        description="The status ailment this move inflicts on its target."
    )
    def resolve_ailment(self, info):
        if not self.move_meta_ailment_id:
            return None
        return info.context.loaders.movemetaailment.load(self.move_meta_ailment_id)

    ailment_chance = Int(
        description="The likelihood this attack will cause an ailment."
    )
    move_meta_category_id = None
    category = Field(
        lazy_import("pokemon_graphql.move_category.types.MoveCategory"),
        description="The category of move this move falls under, e.g. damage or ailment.",
        resolver=lambda root, info: \
            info.context.loaders.movemetacategory.load(root.move_meta_category_id)
    )
    crit_rate = Int(description="Critical hit rate bonus.")
    drain = Int(
        description="HP drain (if positive) or Recoil damage (if negative), in percent of damage done."
    )
    flinch_chance = Int(
        description="The likelihood this attack will cause the target Pokémon to flinch."
    )
    healing = Int(
        description="The amount of hp gained by the attacking Pokemon, in percent of it's maximum HP."
    )
    min_hits = Int(
        description="The minimum number of times this move hits. Null if it always only hits once."
    )
    max_hits = Int(
        description="The maximum number of times this move hits. Null if it always only hits once."
    )
    min_turns = Int(
        description="The minimum number of turns this move continues to take effect. Null if it always only lasts one turn."
    )
    max_turns = Int(
        description="The maximum number of turns this move continues to take effect. Null if it always only lasts one turn."
    )
    stat_chance = Int(
        description="The likelihood this attack will cause a stat change in the target Pokémon."
    )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movemeta.load(id)


class MoveChange(ObjectType):
    accuracy = Int(
        description="The percent value of how likely this move is to be successful."
    )
    move_effect_chance = Int(
        name="effectChance",
        description="The percent value of how likely it is this moves effect will take effect."
    )
    power = Int(
        description="The base power of this move with a value of 0 if it does not have a base power."
    )
    pp = Int(description="Power points. The number of times this move can be used.")
    effect_entries = TranslationList(
        lambda: MoveEffectText,
        description="The effect of this move listed in different languages.",
        resolver=lambda root, info, **kwargs: \
            info.context.loaders.moveeffect_effectentries.load(
                LoaderKey(root.move_effect_id, **kwargs)
            )
    )
    move_effect_id = None
    type_id = None
    type = Field(
        lazy_import("pokemon_graphql.type.types.Type"),
        description="The elemental type of this move."
    )
    def resolve_type(self, info):
        if not self.type_id:
            return None
        return info.context.loaders.type.load(self.type_id)

    version_group_id = None
    version_group = Field(
        lazy_import("pokemon_graphql.version_group.types.VersionGroup"),
        description="The version group in which these move stat values were in effect.",
        resolver=lambda root, info: \
            info.context.loaders.versiongroup.load(root.version_group_id)
    )

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movechange.load(id)


class MoveStatChange(ObjectType):
    change = Int(description="The amount of change.")
    stat_id = None
    stat = Field(
        lazy_import("pokemon_graphql.stat.types.Stat"),
        description="The stat being affected.",
        resolver=lambda root, info: info.context.loaders.stat.load(root.stat_id)
    )

    @classmethod
    def fill(cls, data):
        obj = cls(id=data.id, change=data.change)
        obj.stat_id = data.stat_id
        return obj

    class Meta:
        interfaces = (RelayNode, )

    @classmethod
    def get_node(cls, info, id):
        return info.context.loaders.movemetastatchange.load(id).then(cls.fill)

    @staticmethod
    def fill(data):
        obj = MoveStatChange(id=data.id, change=data.change)
        obj.stat_id = data.stat_id
        return obj
