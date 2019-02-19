from django.contrib import admin

from .models import Profile, LeadAnalyst

from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
admin.site.register(Profile, SimpleHistoryAdmin)
admin.site.register(LeadAnalyst, SimpleHistoryAdmin)
