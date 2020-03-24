from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.shortcuts import redirect
from accounts.models import *

from import_export.admin import ExportActionMixin
from import_export.fields import Field
from import_export import resources


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


class ParticipantInline(admin.StackedInline):
    readonly_fields = ['document', 'gender', 'document_status']
    model = Participant


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
                    'get_document', 'account_actions')
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
            print(obj.participant.document_status)
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
                                                                      args=str(obj.pk)) + '">عدم تایید</a>' + '&nbsp;'
                                 '<a class="button" href="' + reverse('admin:pend_member',
                                                                       args=str(obj.pk)) + '">در حال بررسی</a>')
            elif obj.participant.document_status == 'Rejected':
                return mark_safe('<a class="button" href="' + reverse('admin:verify_member',
                                                                      args=str(obj.pk)) + '">تایید</a>' + '&nbsp;'
                                 '<a class="button" href="' + reverse('admin:pend_member',
                                                                       args=str(obj.pk)) + '">در حال بررسی</a>')
            else:
                return mark_safe('<a class="button" href="' + reverse('admin:verify_member',
                                                                      args=str(obj.pk)) + '">تایید</a>' + '&nbsp;'
                                 '<a class="button" href="' + reverse('admin:unverify_member',
                                                                       args=str(obj.pk)) + '">عدم تایید</a>')
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

    get_school.short_description = 'SCHOOL'
    get_city.short_description = 'CITY'
    get_is_paid.boolean = True
    get_is_paid.short_description = 'IS PAID'
    get_document_status.boolean = True
    get_document_status.short_description = 'IS VERIFIED'
    get_document.short_description = 'DOCUMENT'
    account_actions.short_description = 'VERIFY'


class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_real_name', 'desc')

    def get_username(self, obj):
        return obj.participant.member.username

    def get_real_name(self, obj):
        return obj.participant.member.first_name

    get_username.short_description = 'USERNAME'
    get_real_name.short_description = 'REAL NAME'


admin.site.register(Member, MemberAdmin)
# admin.site.register(Participant)
admin.site.register(Judge)
admin.site.register(PaymentAttempt, PaymentAttemptAdmin)
