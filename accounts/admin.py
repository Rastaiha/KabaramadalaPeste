from django.contrib import admin

# Register your models here.

from django.contrib import admin
from accounts.models import *


admin.site.register(Member)
admin.site.register(Participant)
admin.site.register(Judge)
admin.site.register(PaymentAttempt)
