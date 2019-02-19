"""Expose models to admin interface."""
from django.contrib import admin

from .models.job_member import JobMember, Role
from .models.internal_score_data import (
    InternalScoreData,
    InternalScoreDataFactor,
    InternalScoreDataSubfactor
)
from .models.methodology import RatingDecisionMethodologyLink
from .models.process import Process
from .models.rating_decision import (
    EventType,
    RatingDecision,
    RatingType
)
from .models.rating_decision_issue import RatingDecisionIssue
from .models.questions import (
    Stage,
    Question,
    ControlQuestion
)
from .models.temporary_storage import Tmp
from .models.insider_link import RatingDecisionInsiderLink
from .models.view_log import ViewLog
from .models.press_release import PressRelease
from .models.decision_attributes import DecisionAttributes
from .models.issue_decision import IssueDecision
from rating_process.models.rating_decision_issue_link_attribute import (
    IssueDecisionAttribute
)
from simple_history.admin import SimpleHistoryAdmin


admin.site.register(EventType)
admin.site.register(RatingType)
admin.site.register(RatingDecision, SimpleHistoryAdmin)
admin.site.register(JobMember)
admin.site.register(InternalScoreData, SimpleHistoryAdmin)
admin.site.register(InternalScoreDataFactor)
admin.site.register(InternalScoreDataSubfactor)
admin.site.register(RatingDecisionIssue, SimpleHistoryAdmin)
admin.site.register(Role)
admin.site.register(RatingDecisionMethodologyLink)
admin.site.register(Process, SimpleHistoryAdmin)
admin.site.register(Stage)
admin.site.register(Question)
admin.site.register(ControlQuestion, SimpleHistoryAdmin)
admin.site.register(Tmp)
admin.site.register(RatingDecisionInsiderLink)
admin.site.register(ViewLog)
admin.site.register(PressRelease)
admin.site.register(DecisionAttributes)
admin.site.register(IssueDecision)
admin.site.register(IssueDecisionAttribute)
