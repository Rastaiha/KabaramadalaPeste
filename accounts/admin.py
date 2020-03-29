from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.shortcuts import redirect

from accounts.models import *
from kabaramadalapeste.models import ParticipantPropertyItem
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from import_export.admin import ExportActionMixin
from import_export.fields import Field
from import_export import resources
from notifications.admin import NotificationAdmin
from notifications.models import Notification


class MemberResource(resources.ModelResource):
    gender = Field()
    city = Field()
    school = Field()
    phone_number = Field()
    is_paid = Field()

    class Meta:
        model = Member

    def dehydrate_school(self, member):
        try:
            return member.participant.school
        except Exception:
            return ''

    def dehydrate_is_paid(self, member):
        try:
            return member.participant.is_activated
        except Exception:
            return ''

    def dehydrate_phone_number(self, member):
        try:
            return member.participant.phone_number
        except Exception:
            return ''

    def dehydrate_gender(self, member):
        try:
            return member.participant.gender
        except Exception:
            return ''

    def dehydrate_city(self, member):
        try:
            return member.participant.city
        except Exception:
            return ''


class ParticipantPropertyItemInline(NestedStackedInline):
    model = ParticipantPropertyItem


class ParticipantInline(admin.StackedInline):
    readonly_fields = ['document', 'gender', 'currently_at_island']
    model = Participant
    # inlines = [ParticipantPropertyItemInline]


class IsPaidFilter(admin.SimpleListFilter):
    title = 'is_paid'
    parameter_name = 'is_paid'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(participant__is_activated=True)
        elif value == 'No':
            return queryset.exclude(participant__is_activated=True)
        return queryset


class IsVerifiedFilter(admin.SimpleListFilter):
    title = 'verified'
    parameter_name = 'is_verified'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('Pending', 'Pending'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(participant__document_status='Verified')
        elif value == 'No':
            return queryset.filter(participant__document_status='Rejected')
        elif value == 'Pending':
            return queryset.filter(participant__document_status='Pending')
        return queryset


class MemberAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = MemberResource

    list_display = ('username', 'real_name', 'get_city', 'get_school', 'is_active', 'get_is_paid', 'get_document_status',
                    'get_document', 'account_actions', 'get_has_seen_day1', 'get_has_seen_day2')
    list_filter = ('is_active', IsPaidFilter, IsVerifiedFilter)
    readonly_fields = ['username', 'email']
    fields = ['first_name', 'username', 'email', 'is_active', 'is_participant']
    inlines = [ParticipantInline]

    def get_city(self, obj):
        try:
            return obj.participant.city
        except:
            return None

    def get_school(self, obj):
        try:
            return obj.participant.school
        except:
            return None

    def real_name(self, obj):
        return obj.first_name

    def get_is_paid(self, obj):
        try:
            return obj.participant.is_activated
        except:
            return False

    def get_document_status(self, obj):
        try:
            if 'Pending' in obj.participant.document_status:
                return None
            return obj.participant.document_status == 'Verified'
        except:
            return None

    def get_document(self, obj):
        try:
            return mark_safe('<a class="button" href="' + obj.participant.document.url + '">دیدن مدرک</a>')
        except:
            return None

    def account_actions(self, obj):
        try:
            if obj.participant.document_status == 'Verified':
                return mark_safe('<a class="button" href="' + reverse('admin:unverify_member',
                                                                      args=[obj.pk]) + '">عدم تایید</a>' + '&nbsp;'
                                 '<a class="button" href="' + reverse('admin:pend_member',
                                                                       args=[obj.pk]) + '">در حال بررسی</a>')
            elif obj.participant.document_status == 'Rejected':
                return mark_safe('<a class="button" href="' + reverse('admin:verify_member',
                                                                      args=[obj.pk]) + '">تایید</a>' + '&nbsp;'
                                 '<a class="button" href="' + reverse('admin:pend_member',
                                                                       args=[obj.pk]) + '">در حال بررسی</a>')
            else:
                return mark_safe('<a class="button" href="' + reverse('admin:verify_member',
                                                                      args=[obj.pk]) + '">تایید</a>' + '&nbsp;'
                                 '<a class="button" href="' + reverse('admin:unverify_member',
                                                                       args=[obj.pk]) + '">عدم تایید</a>')
        except:
            return None

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'verify/<int:pk>/',
                self.verify_member,
                name='verify_member',
            ),
            path(
                'unverify/<int:pk>/',
                self.unverify_member,
                name='unverify_member',
            ),
            path(
                'pend/<int:pk>/',
                self.pend_member,
                name='pend_member',
            ),
        ]
        return custom_urls + urls

    def verify_member(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs['pk'])
        member.participant.document_status = 'Verified'
        member.participant.save()
        return redirect('/admin/accounts/member/')

    def unverify_member(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs['pk'])
        member.participant.document_status = 'Rejected'
        member.participant.save()
        return redirect('/admin/accounts/member/')

    def pend_member(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs['pk'])
        member.participant.document_status = 'Pending'
        member.participant.save()
        return redirect('/admin/accounts/member/')

    def get_has_seen_day1(self, obj):
        return Notification.objects.filter(
            unread=False,
            verb='inform',
            timestamp__day=28,
            timestamp__month=3,
            timestamp__year=2020,
            recipient=obj
        ).all().count() > 0

    def get_has_seen_day2(self, obj):
        return Notification.objects.filter(
            unread=False,
            verb='inform',
            timestamp__day=29,
            timestamp__month=3,
            timestamp__year=2020,
            recipient=obj
        ).all().count() > 0

    get_school.short_description = 'SCHOOL'
    get_city.short_description = 'CITY'
    get_is_paid.boolean = True
    get_is_paid.short_description = 'IS PAID'
    get_document_status.boolean = True
    get_document_status.short_description = 'IS VERIFIED'
    get_document.short_description = 'DOCUMENT'
    account_actions.short_description = 'VERIFY'
    get_has_seen_day1.boolean = True
    get_has_seen_day1.short_description = 'SEEN DAY 1'
    get_has_seen_day2.boolean = True
    get_has_seen_day2.short_description = 'SEEN DAY 2'


class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_real_name', 'desc')

    def get_username(self, obj):
        return obj.participant.member.username

    def get_real_name(self, obj):
        return obj.participant.member.first_name

    get_username.short_description = 'USERNAME'
    get_real_name.short_description = 'REAL NAME'


@admin.register(NotificationData)
class NotificationDataAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipients',)
    list_display = (
        'id', 'level', 'text', 'send_to_all_participants', 'get_recipients_count', 'status', 'sent_at', 'send_action'
    )
    exclude = ('status', 'sent_at', 'sent_by')

    def get_recipients_count(self, obj):
        return obj.recipients.count()

    get_recipients_count.short_description = 'recipients count if specific'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'send/<int:pk>/',
                self.send_notifications,
                name='send_notifications',
            ),
        ]
        return custom_urls + urls

    def send_action(self, obj):
        try:
            if obj.status == NotificationData.NotificationStatus.Draft:
                return mark_safe('<a class="button" href="' + reverse('admin:send_notifications',
                                                                      args=[obj.pk]) + '">ارسال</a>')
        except Exception:
            return ''

    def send_notifications(self, request, pk):
        notification_data = NotificationData.objects.get(pk=pk)
        notification_data.send_notifications(request.user)
        return redirect('/admin/accounts/notificationdata/')


class CustomNotificationAdmin(NotificationAdmin):
    list_display = (
        *NotificationAdmin.list_display, 'verb'
    )
    list_filter = (
        'verb', *NotificationAdmin.list_filter
    )
    search_fields = ('recipient__username', 'description', 'data')


admin.site.unregister(Notification)
admin.site.register(Notification, CustomNotificationAdmin)
admin.site.register(Member, MemberAdmin)
# admin.site.register(Participant)
admin.site.register(Judge)
admin.site.register(PaymentAttempt, PaymentAttemptAdmin)
