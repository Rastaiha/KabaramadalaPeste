from django.contrib import admin

# Register your models here.
from kabaramadalapeste.models import (
    Island, Challenge, ChallengeRewardItem, ShortAnswerQuestion, JudgeableQuestion
)
from django.forms.models import BaseInlineFormSet


class RewardInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = list(map(lambda x: {'reward_type': x},
                                     ChallengeRewardItem.REWARD_TYPE_CHOICES))
        super(RewardInlineFormSet, self).__init__(*args, **kwargs)


class ChallengeRewardInline(admin.TabularInline):
    model = ChallengeRewardItem
    min_num = len(ChallengeRewardItem.REWARD_TYPE_CHOICES)
    extra = 0
    formset = RewardInlineFormSet


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


admin.site.register(Island)
