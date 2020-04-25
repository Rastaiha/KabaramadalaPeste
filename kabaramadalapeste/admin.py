from django.contrib import admin
from django.db import transaction
from django.urls import path, reverse
from django.shortcuts import redirect
# Register your models here.
from kabaramadalapeste.models import (
    Island, Challenge, ChallengeRewardItem, ShortAnswerQuestion, JudgeableQuestion,
    TreasureRewardItem, TreasureKeyItem, Treasure, Way, JudgeableSubmit,
    BaseSubmit, TradeOffer, TradeOfferRequestedItem, TradeOfferSuggestedItem,
    AbilityUsage, BandargahConfiguration, BandargahInvestment, Bully, ParticipantIslandStatus,
    PesteConfiguration, GameEventLog
)
from kabaramadalapeste.conf import settings
from django.utils import timezone
from django.forms.models import BaseInlineFormSet
from solo.admin import SingletonModelAdmin
from django.utils.safestring import mark_safe


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
    ordering = ('submitted_at',)
    exclude = ('judged_at', 'pis', 'judged_by')
    readonly_fields = (
        'get_username', 'submitted_answer', 'submitted_at', 'get_challenge_name', 'get_question_title',
        'get_question_file'
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(JudgeableSubmitAdmin, self).get_search_results(
            request, queryset, search_term
        )
        try:
            queryset |= self.model.objects.filter(
                submit_status=BaseSubmit.SubmitStatus.Pending,
                pis__judgeable_question__challenge__name__contains=search_term
            )
            queryset |= self.model.objects.filter(
                submit_status=BaseSubmit.SubmitStatus.Pending,
                pis__judgeable_question__title__contains=search_term
            )
            queryset |= self.model.objects.filter(
                submit_status=BaseSubmit.SubmitStatus.Pending,
                pis__participant__member__username__contains=search_term
            )
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

    def get_question_file(self, obj):
        try:
            return mark_safe('<a href="' + obj.pis.question.question.url + '">صورت سوال</a>')
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
                obj.give_rewards_to_participant()
                obj.pis.participant.send_msg_correct_judged_answer(obj)
                GameEventLog.objects.create(
                    who=obj.pis.participant,
                    when=timezone.now(),
                    where=obj.pis.island,
                    event_type=GameEventLog.EventTypes.JudgeCorrect,
                    related=obj
                )
            elif (obj.initial_submit_status == BaseSubmit.SubmitStatus.Pending and
                    obj.submit_status == BaseSubmit.SubmitStatus.Wrong):
                obj.pis.participant.send_msg_wrong_judged_answer(obj)
                GameEventLog.objects.create(
                    who=obj.pis.participant,
                    when=timezone.now(),
                    where=obj.pis.island,
                    event_type=GameEventLog.EventTypes.JudgeWrong,
                    related=obj
                )
            if obj.submit_status != BaseSubmit.SubmitStatus.Pending:
                obj.judged_at = timezone.now()
                obj.judged_by = request.user
            obj.save()

    get_username.short_description = 'Username'
    get_challenge_name.short_description = 'Challenge'
    get_question_title.short_description = 'Question'
    get_question_file.short_description = 'Question File'


class TradeOfferSuggestedItemInline(admin.StackedInline):
    model = TradeOfferSuggestedItem


class TradeOfferRequestedItemInline(admin.StackedInline):
    model = TradeOfferRequestedItem


@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('creator_participant', 'status', 'creation_datetime', 'close_datetime', 'accepted_participant')
    list_filter = ('status', )
    search_fields = ('creator_participant__member__username', 'accepted_participant__member__username')
    inlines = [TradeOfferRequestedItemInline, TradeOfferSuggestedItemInline]


@admin.register(BandargahConfiguration)
class BandargahConfigurationAdmin(SingletonModelAdmin):
    change_form_template = 'admin/kabaramadalapeste/BandargahConfiguration/change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'compute_bandargah/',
                self.compute_bandargah,
                name='compute_bandargah',
            ),
        ]
        return custom_urls + urls

    @transaction.atomic
    def compute_bandargah(self, request, *args, **kwargs):
        not_applied_investments = BandargahInvestment.objects.filter(is_applied=False).all()
        s = 0
        for investment in not_applied_investments:
            s += investment.amount
        if BandargahConfiguration.get_solo().min_interval_investments < s < BandargahConfiguration.get_solo().max_interval_investments:
            for investment in not_applied_investments:
                investment.participant.add_property(
                    settings.GAME_SEKKE, int(BandargahConfiguration.get_solo().profit_coefficient * investment.amount))
                investment.participant.send_msg_bandargah_computed(investment, True, s)
        else:
            for investment in not_applied_investments:
                investment.participant.add_property(
                    settings.GAME_SEKKE, int(BandargahConfiguration.get_solo().loss_coefficient * investment.amount))
                investment.participant.send_msg_bandargah_computed(investment, False, s)
        not_applied_investments.update(is_applied=True)
        return redirect('/admin/')


@admin.register(AbilityUsage)
class AbilityUsageAdmin(admin.ModelAdmin):
    list_display = ('participant', 'datetime', 'ability_type', 'is_active')
    list_filter = ('ability_type', 'is_active')
    search_fields = ('participant__member__username',)


@admin.register(Bully)
class BullyAdmin(admin.ModelAdmin):
    list_display = ('owner', 'island', 'creation_datetime', 'is_expired', 'expired_datetime')
    list_filter = ('is_expired', 'island',)
    search_fields = ('owner__member__username',)


@admin.register(BandargahInvestment)
class BandargahInvestmentAdmin(admin.ModelAdmin):
    list_display = ('participant', 'amount', 'datetime', 'is_applied')
    list_filter = ('is_applied',)
    search_fields = ('participant__member__username',)


@admin.register(PesteConfiguration)
class PesteConfigurationAdmin(SingletonModelAdmin):
    pass


admin.site.register(Island)
admin.site.register(Way)
admin.site.register(ParticipantIslandStatus)
