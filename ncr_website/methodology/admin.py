"""Expose models to admin interface."""
from django.contrib import admin

from .models import Methodology, MethodologyCategory

# Register your models here.
admin.site.register(MethodologyCategory)
admin.site.register(Methodology)
