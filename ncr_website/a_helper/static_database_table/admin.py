"""Expose models to admin interface."""
from django.contrib import admin
from .models.gics import (
    GICSSector,
    GICSIndustryGroup,
    GICSIndustry,
    GICSSubIndustry
)
from .models.country import (
    CountryRegion
)
from .models.currency import (
    Currency
)
from .models.rating_scale import (
    RatingScale,
    RatingNotch,
    RatingScope,
    RatingCategory
)
from .models.issuer_rating import IssuerRating
from .models.cra_info import CRAInfo

# Register your models here.
admin.site.register(GICSSector)
admin.site.register(GICSIndustryGroup)
admin.site.register(GICSIndustry)
admin.site.register(GICSSubIndustry)
admin.site.register(CountryRegion)
admin.site.register(Currency)
admin.site.register(RatingScale)
admin.site.register(RatingNotch)
admin.site.register(RatingScope)
admin.site.register(RatingCategory)
admin.site.register(IssuerRating)
admin.site.register(CRAInfo)
