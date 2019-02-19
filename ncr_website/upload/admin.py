"""Expose models to admin interface."""
from django.contrib import admin

from .models import AnalyticalDocument, DocumentType, SecurityClass

# Register your models here.
admin.site.register(AnalyticalDocument)
admin.site.register(DocumentType)
admin.site.register(SecurityClass)
