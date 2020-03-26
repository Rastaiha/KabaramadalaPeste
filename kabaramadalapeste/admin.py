from django.contrib import admin
from django.db import transaction
# Register your models here.
from kabaramadalapeste.models import (
    Island, Challenge, ChallengeRewardItem, ShortAnswerQuestion, JudgeableQuestion,
    TreasureRewardItem, TreasureKeyItem, Treasure, Way, JudgeableSubmit,
    BaseSubmit
)
from kabaramadalapeste.conf import settings
from django.utils import timezone
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
    extra = 0
    formset = TreasureRewardInlineFormSet


@admin.register(Treasure)
class TreasureAdmin(admin.ModelAdmin):
    inlines = [
        TreasureKeyInline, TreasureRewardInline,
    ]


@admin.register(JudgeableSubmit)
class JudgeableSubmitAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'scripts/admin-confirm.js',
        )
    list_display = ('get_username', 'submitted_at', 'get_challenge_name', 'get_question_title',)
    search_fields = ('submit_status', )
    exclude = ('judged_at', 'pis', )
    readonly_fields = ('submitted_answer', 'submitted_at', 'get_challenge_name', 'get_question_title')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(JudgeableSubmitAdmin, self).get_search_results(
            request, queryset, search_term
        )
        try:
            queryset |= self.model.objects.filter(pis__judgeable_question__challenge__name__contains=search_term)
            queryset |= self.model.objects.filter(pis__judgeable_question__title__contains=search_term)
            queryset |= self.model.objects.filter(pis__participant__member__username__contains=search_term)
        except Exception:
            pass
        return queryset, use_distinct

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(submit_status=BaseSubmit.SubmitStatus.Pending)

    def get_username(self, obj):
        try:
            return obj.pis.participant.member.username
        except Exception:
            return ''

    def get_challenge_name(self, obj):
        try:
            return obj.pis.question.challenge.name
        except Exception:
            return ''

    def get_question_title(self, obj):
        try:
            return obj.pis.question.title
        except Exception:
            return ''

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if (obj.initial_submit_status == BaseSubmit.SubmitStatus.Pending and
                    obj.submit_status == BaseSubmit.SubmitStatus.Correct):
                for reward in obj.pis.question.challenge.rewards.all():
                    obj.pis.participant.add_property(reward.key, reward.amount)
            obj.judged_at = timezone.now()
            obj.save()

    get_username.short_description = 'Username'
    get_challenge_name.short_description = 'Challenge'
    get_question_title.short_description = 'Question'


admin.site.register(Island)
admin.site.register(Way)
