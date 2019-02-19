"""Misc functions to return correct values for ESMA reporting."""
from rating_process.models.press_release import PressRelease
from rating_process.util import get_public_external_report
from django.apps import apps


# Used to dynamically load model below
get_model = apps.get_model


def press_release_data(decision_obj):
    """Get press release information
    :param obj decision_obj: a RatingDecision object
    :returns: (tuple) Press release object and boolean if the press release
                node should be created.
    """

    try:
        press_release = PressRelease.objects.get(
            rating_decision=decision_obj)
        press_release_flag = True

    except PressRelease.DoesNotExist:
        press_release = None
        press_release_flag = False

    return press_release, press_release_flag


def research_report_data(decision_obj):
    """Get the external rating research report.
    :param obj decision_obj: a RatingDecision object
    :returns: (tuple) AnalyticalDocument object and boolean if the
                research report node should be created.
    """

    try:
        research_report = get_public_external_report(decision_obj)
        research_report_flag = True
    except Exception:

        research_report = None
        research_report_flag = False

    return research_report, research_report_flag


def get_attributes(issues, decision_obj):
    """Get the attributes for a decision object for issuer or issue.
    :param bool issues: True if we are analysing issues
    :param obj decision_obj: RatingDecision or IssueDecision object
    :returns: (obj) Attributes object for either issuer or issue
    """

    if issues:
        # The attribute models have different names for issuer and issue
        attribute_model = get_model('rating_process',
                                    'issuedecisionattribute')

        attributes = attribute_model.objects.get(
            rating_decision_issue=decision_obj)

    else:
        # The attribute models have different names for issuer and issue
        attribute_model = get_model('rating_process',
                                    'decisionattributes')

        attributes = attribute_model.objects.get(
            rating_decision=decision_obj)

    return attributes
