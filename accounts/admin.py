from django.contrib import admin

# Register your models here.

from django.contrib import admin
from accounts.models import *


class MemberAdmin(admin.ModelAdmin):
    list_display = ('username', 'real_name', 'get_city', 'get_school', 'get_is_paid')
    readonly_fields = ['username', 'email']
    fields = ['first_name', 'username', 'email', 'is_active', 'is_participant']

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

    get_school.short_description = 'SCHOOL'
    get_city.short_description = 'CITY'
    get_is_paid.boolean = True
    get_is_paid.short_description = 'IS PAID'


class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_real_name', 'desc')

    def get_username(self, obj):
        return obj.participant.member.username

    def get_real_name(self, obj):
        return obj.participant.member.first_name

    get_username.short_description = 'USERNAME'
    get_real_name.short_description = 'REAL NAME'


admin.site.register(Member, MemberAdmin)
admin.site.register(Participant)
admin.site.register(Judge)
admin.site.register(PaymentAttempt, PaymentAttemptAdmin)
