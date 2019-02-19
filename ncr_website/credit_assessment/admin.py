from django.contrib import admin

from credit_assessment.models.assessment import (
    AssessmentJob
)
from credit_assessment.models.subscores import (
    AssessmentSubscoreData
)
from credit_assessment.models.seniority_level_assessment import (
    SeniorityLevelAssessment
)
from credit_assessment.models.highest_lowest import HighestLowest


# Register your models here.
admin.site.register(AssessmentJob)
admin.site.register(AssessmentSubscoreData)
admin.site.register(SeniorityLevelAssessment)
admin.site.register(HighestLowest)
