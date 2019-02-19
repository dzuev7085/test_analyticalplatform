"""Expose models to admin interface."""
from django.contrib import admin

from .models import (
    Issue,
    Seniority,
    SeniorityLevel,
    Program
)

from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
admin.site.register(Issue, SimpleHistoryAdmin)
admin.site.register(Seniority)
admin.site.register(SeniorityLevel)
admin.site.register(Program)
