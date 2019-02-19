from credit_assessment.models.seniority_level_assessment import (
    SeniorityLevelAssessment
)


def get_issues_relative_level(assessment):
    """Set correct rating for all issue levels."""

    # Store the current assessment level, as we need to get the
    # relative value of each issue level
    # Has to be initialized here, before the rating is updated
    issue_assessment_dict = {}

    # Get all issue levels linked to the current assessment
    i_lvl = SeniorityLevelAssessment.objects.filter(
        assessment=assessment,
    )

    for i in i_lvl:
        issue_assessment_dict[i.id] = assessment.assessment_lt - i.decided_lt

    return issue_assessment_dict
