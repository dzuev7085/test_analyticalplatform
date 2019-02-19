"""Register models with the admin interface."""
from django.contrib import admin

from .models.xml_file import XMLFile
from .models.reporting_type_info import ReportingTypeInfo
from .models.q_lead_analyst import LeadAnalyst
from .models.q_rating_scale import (
    RatingScale,
    RatingCategory,
    RatingNotch,
    RatingScope
)
from .models.q_debt_classification import DebtClassification
from .models.q_issue_program import IssueProgram
from .models.q_issuer_rating import IssuerRating
from .models.q_cra_info import CRAInfo
from .models.qt_rating_action import (
    QTRatingCreateData,
    QTRatingActionInfo,
    QTActionDateInfo,
    QTLeadAnalystInfo,
    QTRatingAction,
    QTRatingValue,
    QTRatingInfo,
    QTIssuerInfo,
    QTPrecedingPreliminaryRating,
    QTInstrumentInfo,
)

admin.site.register(XMLFile)
admin.site.register(ReportingTypeInfo)
admin.site.register(LeadAnalyst)
admin.site.register(RatingScale)
admin.site.register(RatingCategory)
admin.site.register(RatingNotch)
admin.site.register(RatingScope)
admin.site.register(DebtClassification)
admin.site.register(IssueProgram)
admin.site.register(IssuerRating)
admin.site.register(CRAInfo)
admin.site.register(QTRatingCreateData)
admin.site.register(QTRatingActionInfo)
admin.site.register(QTActionDateInfo)
admin.site.register(QTLeadAnalystInfo)
admin.site.register(QTRatingAction)
admin.site.register(QTRatingValue)
admin.site.register(QTRatingInfo)
admin.site.register(QTIssuerInfo)
admin.site.register(QTPrecedingPreliminaryRating)
admin.site.register(QTInstrumentInfo)
