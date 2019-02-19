"""Expose models to admin interface."""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Analyst,
    Event,
    InsiderList,
    Issuer,
    IssuerType,
    OnboardingProcess,
)
from .models.insider_log import InsiderLog
from .models.identifier import Identifier
from .models.address import Address
from .models.classification import Classification

# Register your models here.
admin.site.register(Issuer, SimpleHistoryAdmin)
admin.site.register(IssuerType)
admin.site.register(Analyst, SimpleHistoryAdmin)
admin.site.register(InsiderList, SimpleHistoryAdmin)
admin.site.register(Event)
admin.site.register(OnboardingProcess)
admin.site.register(InsiderLog)
admin.site.register(Identifier)
admin.site.register(Address)
admin.site.register(Classification)
