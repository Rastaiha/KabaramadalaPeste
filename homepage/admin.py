from django.contrib import admin

# Register your models here.

from django.contrib import admin
from solo.admin import SingletonModelAdmin
from homepage.models import *


class SiteConfigAdmin(admin.ModelAdmin):
    pass


admin.site.register(SiteConfiguration, SiteConfigAdmin)
admin.site.register(TeamMember)
