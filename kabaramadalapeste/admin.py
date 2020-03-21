from django.contrib import admin

# Register your models here.
from kabaramadalapeste.models import (
    Island, Challenge, ChallengeRewardItem, ShortAnswerQuestion, JudgeableQuestion,
    TreasureRewardItem, TreasureKeyItem, Treasure
)
from kabaramadalapeste.conf import settings
from django.forms.models import BaseInlineFormSet


class ChallengeRewardInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = list(map(lambda x: {'reward_type': x},
                                     settings.GAME_CHALLENGE_REWARD_TYPE_CHOICES))
        super(ChallengeRewardInlineFormSet, self).__init__(*args, **kwargs)


class ChallengeRewardInline(admin.TabularInline):
    model = ChallengeRewardItem
    min_num = len(settings.GAME_CHALLENGE_REWARD_TYPE_CHOICES)
    extra = 0
    formset = ChallengeRewardInlineFormSet


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    inlines = [
        ChallengeRewardInline,
    ]


@admin.register(ShortAnswerQuestion)
class ShortAnswerQuestionAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['challenge'].queryset = Challenge.objects.filter(is_judgeable=False)
        return super(ShortAnswerQuestionAdmin, self).render_change_form(request, context, *args, **kwargs)


@admin.register(JudgeableQuestion)
class JudgeableQuestionAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['challenge'].queryset = Challenge.objects.filter(is_judgeable=True)
        return super(JudgeableQuestionAdmin, self).render_change_form(request, context, *args, **kwargs)


class TreasureKeyInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = list(map(lambda x: {'key_type': x},
                                     settings.GAME_TREASURE_KEY_TYPE_CHOICES))
        print(kwargs['initial'])
        super(TreasureKeyInlineFormSet, self).__init__(*args, **kwargs)


class TreasureKeyInline(admin.TabularInline):
    model = TreasureKeyItem
    min_num = len(settings.GAME_TREASURE_KEY_TYPE_CHOICES)
    extra = 0
    formset = TreasureKeyInlineFormSet


class TreasureRewardInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = list(map(lambda x: {'reward_type': x},
                                     settings.GAME_TREASURE_REWARD_TYPE_CHOICES))
        super(TreasureRewardInlineFormSet, self).__init__(*args, **kwargs)


class TreasureRewardInline(admin.TabularInline):
    model = TreasureRewardItem
    min_num = len(settings.GAME_TREASURE_REWARD_TYPE_CHOICES)
    extra = 0
    formset = TreasureRewardInlineFormSet


@admin.register(Treasure)
class TreasureAdmin(admin.ModelAdmin):
    inlines = [
        TreasureKeyInline, TreasureRewardInline,
    ]


admin.site.register(Island)
