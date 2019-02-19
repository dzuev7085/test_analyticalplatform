from django.conf.urls import url

from .views import (
    CommitteeMemberCreateView,
    CommitteeMemberDeleteView,
    InternalScoreDataAdjustmentUpdateView,
    InternalScoreDataSubFactorUpdateView,
    RatingDecisionIssueCreateView,
    RatingDecisionIssueUpdateView,
    RatingDecisionUpdateView,
    RatingProcessCreateView,
    answer_question,
    EditorCreateView,
    AdminControlUpdateView,
    LinkRaingJobInsiderView,
    UnlinkRaingJobInsiderView,
    pending_confirm_parameter,
    confirm_parameter,
    PressReleaseUpdateView,
    ViewRatingJob,
    IssueRatingDecisionAddView,
    IssueRatingDecisionEditView,
)
from upload.views import RatingDecisionDocument


urlpatterns = [
    # Send data to update subfactor
    url(r'^rating/update/subfactor/(?P<subscore_pk>\d+)/(?P<decided>\d+)/'
        r'(?P<edit_weight>\d+)/$',
        InternalScoreDataSubFactorUpdateView.as_view(),
        name="rating_score_subfactor_update"),

    # Send data to update adjustment
    url(r'^rating/update/adjustment/(?P<subscore_pk>\d+)/(?P<decided>\d+)/$',
        InternalScoreDataAdjustmentUpdateView.as_view(),
        name="rating_score_adjustment_update"),

    # Send data to update attribute of rating component
    url(r'^rating/update/(?P<rating_decision_pk>(\d+))/'
        '(?P<field>.*)/$',
        RatingDecisionUpdateView.as_view(),
        name='rating_decision_update_field'),

    # Send data to update attribute of rating component
    url(r'^rating_job/view/(?P<pk>\d+)/(?P<rating_decision_pk>(\d+))/$',
        ViewRatingJob.as_view(),
        name='rating_decision_view'),

    # Add a new member of a committee
    url(r'^rating/committee/add/(?P<rating_decision_pk>(\d+))/',
        CommitteeMemberCreateView.as_view(),
        name="rating_committee_member_add"),

    # Delete an insider from the database
    url(r'^rating/committee/delete/(?P<committee_member_id>\d+)/$',
        CommitteeMemberDeleteView.as_view(),
        name="rating_committee_member_delete"),

    # Delete an insider from the database
    url(r'^rating/new/(?P<issuer_pk>\d+)/$',
        RatingProcessCreateView.as_view(),
        name="rating_decision_new"),

    # Add a new issue seniority
    url(r'^rating/issue/add/(?P<rating_decision_pk>(\d+))/',
        RatingDecisionIssueCreateView.as_view(),
        name="rating_issue_add"),

    # Add a new issue seniority
    url(r'^rating/issue/edit/(?P<rating_decision_issue_pk>(\d+))/'
        r'(?P<decided>\d+)/$',
        RatingDecisionIssueUpdateView.as_view(),
        name="rating_issue_edit"),

    # Update a question
    url(r'^rating/question/update/(?P<control_question_pk>(\d+))/'
        r'/(?P<step>(\d+))/$',
        answer_question,
        name="answer_question"),

    # Add a document
    url(r'^rating/document/add/(?P<document_type_pk>(\d+))/'
        r'(?P<rating_decision_pk>(\d+))/'
        r'(?P<issuer_pk>(\d+))/'
        r'(?P<security_class>(\d+))/$',
        RatingDecisionDocument.as_view(),
        name="rating_decision_document_add"),

    url(r'^issuer/rating_job/editor/add/(?P<rating_decision_pk>(\d+))/',
        EditorCreateView.as_view(),
        name="issuer_rating_job_editor_add"),

    # Update links to admin control
    url(r'^issuer/rating_job/admincontrol/update/(?P<tmp_pk>(\d+))/'
        r'(?P<mode>(\d+))/$',
        AdminControlUpdateView.as_view(),
        name="issuer_rating_job_admincontrol_update"),

    # Link rating decision and issuer insider
    url(r'^issuer/rating_job/insider/add/(?P<rating_decision_pk>(\d+))/$',
        LinkRaingJobInsiderView.as_view(),
        name="issuer_rating_job_insider_add"),

    # Link rating decision and issuer insider
    url(r'^issuer/rating_job/insider/delete/(?P<pk>(\d+))/$',
        UnlinkRaingJobInsiderView.as_view(),
        name="issuer_rating_job_insider_delete"),

    # Decisions pending some of the stages before publishing
    url(r'^rating/committee/pending/update/(?P<action>.*)/'
        r'(?P<rating_decision_pk>(\d+))/$',
        pending_confirm_parameter,
        name="rating_committee_pending_action"),

    # Confirm a parameter
    url(r'^issuer/rating_job/confirm_parameter/'
        r'(?P<pk>(\d+))/$',
        confirm_parameter,
        name="rating_decision_confirm_parameter"),

    # Update press release
    url(r'^issuer/rating_job/press_release/(?P<press_release_pk>(\d+))/'
        '(?P<field>.*)/$',
        PressReleaseUpdateView.as_view(),
        name='issuer_rating_job_press_release_update'),

    # Add rating for an issue
    url(r'^issuer/rating_job/issue/add/(?P<issue_pk>(\d+))'
        r'/(?P<rating_decision_pk>(\d+))/$',
        IssueRatingDecisionAddView.as_view(),
        name="issuer_rating_job_add_issue_decision"),

    # Edit rating for an issue
    url(r'^issuer/rating_job/issue/edit/(?P<issue_decision_pk>(\d+))/$',
        IssueRatingDecisionEditView.as_view(),
        name="issuer_rating_job_edit_issue_decision"),

]
