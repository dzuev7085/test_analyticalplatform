from django.shortcuts import redirect
import pytz
import os
from datetime import timedelta

from a_helper.modal_helper.views import (
    AjaxCreateView,
    AjaxDeleteView,
    AjaxUpdateView
)
from issuer.models import Event, Issuer
from gui.templatetags.template_tags import format_reference_number
from rating_process.models.issue_decision import IssueDecision

from rating_process.forms import (
    AddCommitteeMemberForm,
    EditDecidedAdjustmentFactor,
    EditDecidedSubfactor,
    EditProposedAdjustmentFactor,
    EditProposedSubfactor,
    EditRatingDecision,
    RatingDecisionIssueAddSeniority,
    RatingDecisionIssueEditDecided,
    RatingDecisionIssueEditProposed,
    StartRatingProcess,
    AddEditorForm,
    UpdateAdminControlEditorForm,
    UpdateAdminControlIssuerForm,
    RatingDecisionInsiderLinkForm,
    EditPressReleaseForm,
    IssueRatingDecisionAddForm,
    IssueRatingDecisionEditForm
)
from .models.job_member import JobMember, Group, Role
from .models.internal_score_data import InternalScoreData
from .models.rating_decision import RatingDecision
from .models.rating_decision_issue import RatingDecisionIssue
from .models.questions import ControlQuestion
from .models.temporary_storage import Tmp
from .models.process import Process
from .models.insider_link import RatingDecisionInsiderLink
from .models.press_release import PressRelease
from rating_process.tasks import refresh_issue_decision_attributes
from integrations.mailchimp.tasks import run_create_campaign
from django.contrib import messages

from .tasks import refresh_decision_attributes, update_issue_rating

from a_helper.mail.tasks import send_email, send_outlook_invitation

from .util import send_public_report
from django.views.generic import DetailView
from rating.util.generate_context import return_company_context

from django.utils import timezone
from django import http
from .const import (
    SETUP_HEADER,
    SETUP_BODY,
    PRE_COMMITTEE_HEADER,
    PRE_COMMITTEE_BODY,
    ANALYTICAL_PHASE_HEADER,
    ANALYTICAL_PHASE_BODY,
    CHAIR_FINAL_APPROVAL_BODY,
    CHAIR_FINAL_APPROVAL_HEADER,
    ANALYST_FINAL_APPROVAL_BODY,
    ANALYST_FINAL_APPROVAL_HEADER,
    EDITOR_EMAIL,
    EDITOR_HEADER,
    MEMBER_ADDED_HEADER,
    MEMBER_ADDED_BODY,
    ISSUE_DECISION_HEADER,
    ISSUE_DECISION_BODY
)


# pylint: disable=too-many-ancestors
class RatingProcessCreateView(AjaxCreateView):
    """RatingProcessCreateView."""

    form_class = StartRatingProcess

    def get_success_url(self):
        """Custom get_success_url method."""
        return self.request.META.get('HTTP_REFERER') + '#score'

    def get_form_kwargs(self):
        """Custom get_form_kwargs method."""

        kwargs = super(RatingProcessCreateView, self).get_form_kwargs()
        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_valid(self, form):
        """Custom form_valid method."""

        issuer_id = self.kwargs['issuer_pk']
        issuer_obj = Issuer.objects.get(id=issuer_id)

        obj = form.save(commit=False)
        obj.issuer = issuer_obj
        obj.initiated_by = self.request.user

        # We need the object instance to save the event, hence saving here
        obj.save()

        # Log the event
        Event.objects.create(
            issuer=issuer_obj,
            event_type_id=24,
            triggered_by_user=self.request.user
        )

        return super(RatingProcessCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class InternalScoreDataSubFactorUpdateView(AjaxUpdateView):
    """InternalScoreDataSubFactorUpdateView view."""

    model = InternalScoreData
    pk_url_kwarg = 'subscore_pk'

    def get_form_class(self):
        if self.kwargs['decided'] == '1':
            return EditDecidedSubfactor
        else:
            return EditProposedSubfactor

    def get_form_kwargs(self):

        kwargs = super(InternalScoreDataSubFactorUpdateView,
                       self).get_form_kwargs()
        kwargs.update({'edit_weight': int(self.kwargs['edit_weight'])})

        return kwargs

    def form_valid(self, form):

        if self.kwargs['decided'] != '1':
            obj = form.save(commit=False)
            obj.decided_score = form.cleaned_data['proposed_score']

            obj.save()

        return super(InternalScoreDataSubFactorUpdateView,
                     self).form_valid(form)


# pylint: disable=too-many-ancestors
class InternalScoreDataAdjustmentUpdateView(AjaxUpdateView):
    """InternalScoreDataAdjustmentUpdateView view."""

    model = InternalScoreData
    pk_url_kwarg = 'subscore_pk'

    def get_form_class(self):
        if self.kwargs['decided'] == '1':
            return EditDecidedAdjustmentFactor
        else:
            return EditProposedAdjustmentFactor

    def form_valid(self, form):

        if self.kwargs['decided'] != '1':
            obj = form.save(commit=False)
            obj.decided_notch_adjustment = form.cleaned_data[
                'proposed_notch_adjustment']

            obj.save()

        return super(InternalScoreDataAdjustmentUpdateView,
                     self).form_valid(form)


# pylint: disable=too-many-ancestors
class RatingDecisionUpdateView(AjaxUpdateView):
    """RatingDecisionUpdateView view."""

    model = RatingDecision
    form_class = EditRatingDecision
    pk_url_kwarg = 'rating_decision_pk'

    def get_form_kwargs(self):
        """Custom method for a kwargs to pass to form class."""

        rating_decision_obj = RatingDecision.objects.get(
            id=self.kwargs['rating_decision_pk'])

        kwargs = super(RatingDecisionUpdateView, self).get_form_kwargs()
        kwargs.update(
            {'field': self.kwargs['field'],
             'rating_decision_obj': rating_decision_obj}
        )

        return kwargs

    def form_valid(self, form):
        """Custom method for a valid form."""

        # date_time_committee
        date_time_committee = form.cleaned_data[
                'date_time_committee']

        if date_time_committee is not None:

            # We manually enter a date in Oslo/Stockholm time in the GUI
            # so we need to convert it into UTC
            obj = form.save(commit=False)
            datetime_in_utc = date_time_committee.astimezone(pytz.utc)
            obj.date_time_committee = datetime_in_utc
            obj.save()

        return super(RatingDecisionUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class CommitteeMemberCreateView(AjaxCreateView):
    """CommitteeMemberCreateView view."""

    form_class = AddCommitteeMemberForm

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):
        kwargs = super(CommitteeMemberCreateView, self).get_form_kwargs()

        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        return kwargs

    def form_valid(self, form):

        group_obj = Group.objects.get(pk=1)

        obj = form.save(commit=False)

        rating_decision_obj = form.cleaned_data['rating_decision']

        obj.rating_decision = rating_decision_obj
        obj.group = group_obj

        obj.save()

        r_name = obj.role.role_name.lower()
        if r_name == 'voter':
            role = 'a voter'
        else:
            role = 'an observer'

        # Send notification to analyst
        send_outlook_invitation.delay(
            header=MEMBER_ADDED_HEADER % obj.rating_decision.issuer,
            body=MEMBER_ADDED_BODY % (
                obj.member.first_name,
                self.request.user.first_name,
                role,
                obj.rating_decision.issuer,
            ),
            attendee=obj.member.email,
            start_time=obj.rating_decision.date_time_committee,
            end_time=obj.rating_decision.date_time_committee
        )

        return super(CommitteeMemberCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class EditorCreateView(AjaxCreateView):
    """Add an editor to the rating job."""

    form_class = AddEditorForm

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):
        kwargs = super(EditorCreateView, self).get_form_kwargs()

        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        return kwargs

    def form_valid(self, form):

        obj = form.save(commit=False)

        rating_decision_obj = form.cleaned_data['rating_decision']
        group_obj = Group.objects.get(pk=2)
        role_obj = Role.objects.get(pk=3)

        obj.rating_decision = rating_decision_obj
        obj.group = group_obj
        obj.role = role_obj
        obj.save()

        return super(EditorCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class AdminControlUpdateView(AjaxUpdateView):
    """Add an editor to the rating job."""

    model = Tmp
    pk_url_kwarg = 'tmp_pk'

    def get_form_class(self):

        if self.kwargs['mode'] == '0':
            return UpdateAdminControlEditorForm
        else:
            return UpdateAdminControlIssuerForm

    def form_valid(self, form):

        obj = form.save(commit=False)

        # This is to store a null value if there is no link
        try:
            if len(obj.editor_admin_control_link) == 0:
                obj.editor_admin_control_link = None
        except:  # noqa E722
            obj.editor_admin_control_link = None

        try:
            if len(obj.issuer_admin_control_link) == 0:
                obj.issuer_admin_control_link = None
        except:  # noqa E722
            obj.issuer_admin_control_link = None

        obj.save()

        return super(AdminControlUpdateView, self).form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


# pylint: disable=too-many-ancestors
class CommitteeMemberDeleteView(AjaxDeleteView):
    model = JobMember
    pk_url_kwarg = 'committee_member_id'


# pylint: disable=too-many-ancestors
class RatingDecisionIssueCreateView(AjaxCreateView):
    """Add seniority of an issue to the rating decision."""

    form_class = RatingDecisionIssueAddSeniority

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):
        kwargs = super(RatingDecisionIssueCreateView, self).get_form_kwargs()

        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_valid(self, form):

        obj = form.save(commit=False)

        obj.rating_decision = form.cleaned_data['rating_decision']

        return super(RatingDecisionIssueCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class RatingDecisionIssueUpdateView(AjaxUpdateView):
    """RatingDecisionIssueUpdateView view."""

    model = RatingDecisionIssue
    pk_url_kwarg = 'rating_decision_issue_pk'

    def get_form_class(self):

        if self.kwargs['decided'] == '1':
            return RatingDecisionIssueEditDecided
        else:
            return RatingDecisionIssueEditProposed

    def form_valid(self, form):

        if self.kwargs['decided'] != '1':
            obj = form.save(commit=False)
            obj.decided_lt = form.cleaned_data['proposed_lt']

            obj.save()

        return super(RatingDecisionIssueUpdateView, self).form_valid(form)


def answer_question(request, control_question_pk, step):
    """Updates a question during the rating process."""

    control_question_obj = ControlQuestion.objects.get(pk=control_question_pk)

    control_question_obj.answered_on = timezone.now()
    control_question_obj.answered_by = request.user
    control_question_obj.answer_correct = True

    # Save changes
    control_question_obj.save()

    return http.HttpResponseRedirect(request.META.get(
        'HTTP_REFERER', '/') + '#setup_step_' + step)


# pylint: disable=too-many-ancestors
class LinkRaingJobInsiderView(AjaxCreateView):
    """View to add an insider to send list."""

    form_class = RatingDecisionInsiderLinkForm

    def get_form_kwargs(self):
        """Overwrite get_form_kwargs."""

        kwargs = super(LinkRaingJobInsiderView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs


# pylint: disable=too-many-ancestors
class UnlinkRaingJobInsiderView(AjaxDeleteView):
    """View to remove an insider from send list."""

    model = RatingDecisionInsiderLink
    pk_url_kwarg = 'pk'


def pending_confirm_parameter(request, action, rating_decision_pk):
    """Update steps in the rating process model Process."""

    hash = None

    if action:

        rating_decision_obj = RatingDecision.objects.get(pk=rating_decision_pk)

        rating_process_obj, created = Process.objects.get_or_create(
                rating_decision=rating_decision_obj)

        rating_job_id = format_reference_number(number=rating_decision_obj.id,
                                                object_type='rating_decision',)

        if action == 'setup_done':
            hash = 'setup_step_2'

            rating_decision_obj.process_step = 2
            rating_process_obj.setup_done = timezone.now()

            to_list = [
                rating_decision_obj.chair.email
            ]

            # Notify analysts and relationship manager
            cc_list = [
                rating_decision_obj.issuer.analyst.
                primary_analyst.email,
                rating_decision_obj.issuer.analyst.
                secondary_analyst.email,
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                cc_list.append('compliance@nordiccreditrating.com')

            header = SETUP_HEADER.format(
                rating_decision_obj.issuer,
                rating_job_id,
            )
            body = SETUP_BODY % rating_decision_obj.chair.first_name

            # Send notification to chair
            send_email.delay(
                header=header,
                body=body,
                to=to_list,
                from_sender=None,
                cc=cc_list)

        elif action == 'pre_committee_done':
            hash = 'setup_step_3'

            rating_decision_obj.process_step = 3
            rating_process_obj.pre_committee_done = timezone.now()
            rating_decision_obj.chair_confirmed = True
            rating_decision_obj.date_time_committee_confirmed = True

            to_list = [
                rating_decision_obj.issuer.analyst.
                primary_analyst.email,
                rating_decision_obj.issuer.analyst.
                secondary_analyst.email,
            ]
            cc_list = [
                rating_decision_obj.issuer.relationship_manager.email,
                rating_decision_obj.chair.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                cc_list.append('compliance@nordiccreditrating.com')

            header = PRE_COMMITTEE_HEADER.format(
                rating_decision_obj.issuer,
                rating_decision_obj.chair.get_full_name(),
                rating_job_id,
            )

            # Send notification
            send_email.delay(
                header=header,
                body=PRE_COMMITTEE_BODY % rating_decision_obj.issuer.analyst.
                primary_analyst.first_name,
                to=to_list,
                from_sender=None,
                cc=cc_list,)

        elif action == 'analytical_phase_done':
            hash = 'setup_step_4'

            rating_decision_obj.process_step = 4
            rating_process_obj.analytical_phase_done = timezone.now()

            # Send notification to chair and members of committee
            to_list = [
                rating_decision_obj.issuer.analyst.primary_analyst.email,
                rating_decision_obj.issuer.analyst.secondary_analyst.email,
                rating_decision_obj.chair.email,
            ]
            cc_list = [
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                cc_list.append('compliance@nordiccreditrating.com')

            # Get all members
            committee_members = list(
                JobMember.objects.confirmed_members().filter(
                    rating_decision=rating_decision_obj,
                    group_id=1))
            for item in committee_members:
                to_list.append(item.member.email)

            local_dt = timezone.localtime(
                rating_decision_obj.date_time_committee,
                timezone.get_fixed_timezone(60))

            header = ANALYTICAL_PHASE_HEADER.format(
                rating_decision_obj.issuer,
                local_dt.strftime('%Y-%m-%d %H:%M'),
                rating_job_id,
            )

            send_email.delay(
                header=header,
                body=ANALYTICAL_PHASE_BODY,
                to=to_list,
                cc=cc_list,
                from_sender=None)

        elif action == 'post_committee_done':
            hash = 'setup_step_5'

            rating_decision_obj.process_step = 5
            rating_process_obj.post_committee_done = timezone.now()

            # Contains the name and email of the editor
            editor_obj = JobMember.objects.get(
                rating_decision=rating_decision_obj,
                group=Group.objects.get(pk=2))

            to_list = [
                editor_obj.member.email,
            ]
            cc_list = [
                rating_decision_obj.issuer.analyst.primary_analyst.email,
                rating_decision_obj.issuer.analyst.secondary_analyst.email,
                rating_decision_obj.chair.email,
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                cc_list.append('compliance@nordiccreditrating.com')

            header = EDITOR_HEADER.format(
                rating_decision_obj.issuer,
                rating_job_id,
            )

            # Send email with link to admin control to editor
            send_email.delay(header=header,
                             body=EDITOR_EMAIL % (
                                 editor_obj.member.first_name,
                                 rating_decision_obj.issuer.analyst.
                                 primary_analyst.first_name),
                             to=to_list,
                             cc=cc_list,
                             from_sender=None,)

        elif action == 'editor_phase_done':
            """Here, we're sending the draft report to the issuer."""

            hash = 'setup_step_6'

            rating_decision_obj.process_step = 6

            # External analysis
            send_public_report(rating_decision_obj)

            # Send notification to chair
            to_list = [
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            header = "{} | the draft report has been sent to the " \
                     "issuer".format(rating_decision_obj.issuer,)

            send_email.delay(
                header=header,
                body=' ',
                to=to_list,
                from_sender=None,)

            # Set a timestamp when se sent the report to the issuer
            rating_decision_obj.date_time_communicated_issuer = timezone.now()
            rating_process_obj.editor_review_done = timezone.now()

        elif action == 'issuer_confirmation_phase_done':
            hash = 'setup_step_7'

            rating_decision_obj.process_step = 7

            to_list = [
                rating_decision_obj.chair.email,
                rating_decision_obj.issuer.analyst.primary_analyst.email,
                rating_decision_obj.issuer.analyst.secondary_analyst.email,
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                to_list.append('compliance@nordiccreditrating.com')

            header = "{} | The issuer has confirmed the accuracy of the " \
                     "draft report for rating job {}".format(
                        rating_decision_obj.issuer,
                        rating_job_id, )

            # Send notification
            send_email.delay(
                header=header,
                body='',
                to=to_list,
                from_sender=None,)

            rating_process_obj.issuer_confirmation_done = timezone.now()

        elif action == 'analyst_final_approval_phase_done':
            hash = 'setup_step_8'

            rating_process_obj.final_sign_off_analyst_done = timezone.now()
            rating_decision_obj.process_step = 8

            to_list = [
                rating_decision_obj.issuer.analyst.primary_analyst.email,
            ]
            cc_list = [
                rating_decision_obj.chair.email,
                rating_decision_obj.issuer.analyst.secondary_analyst.email,
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                cc_list.append('compliance@nordiccreditrating.com')

            header = ANALYST_FINAL_APPROVAL_HEADER.format(
                rating_decision_obj.issuer
            )

            # Send notification to chair
            send_email.delay(
                header=header,
                body=ANALYST_FINAL_APPROVAL_BODY %
                rating_decision_obj.issuer.analyst.
                primary_analyst.first_name,
                to=to_list,
                from_sender=None,
                cc=cc_list)

        elif action == 'chair_final_approval_phase_done':
            hash = 'setup_step_9'

            rating_decision_obj.process_step = 9
            rating_process_obj.final_sign_off_chair_done = timezone.now()

            to_list = [
                rating_decision_obj.issuer.analyst.primary_analyst.email,
                rating_decision_obj.issuer.analyst.secondary_analyst.email,
            ]
            cc_list = [
                rating_decision_obj.chair.email,
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                cc_list.append('compliance@nordiccreditrating.com')

            header = CHAIR_FINAL_APPROVAL_HEADER.format(
                rating_decision_obj.issuer
            )

            # Send notification to analyst
            send_email.delay(header=header,
                             body=CHAIR_FINAL_APPROVAL_BODY %
                             rating_decision_obj.issuer.analyst.
                             primary_analyst.first_name,
                             to=to_list,
                             from_sender=None,
                             cc=cc_list,)

        elif action == 'publishing_phase_done':
            hash = ""

            rating_decision_obj.date_time_published = timezone.now()

            to_list = [
                rating_decision_obj.issuer.analyst.primary_analyst.email,
                rating_decision_obj.issuer.analyst.secondary_analyst.email,
                rating_decision_obj.chair.email,
                rating_decision_obj.issuer.relationship_manager.email,
            ]

            # We want to notify Compliance in production
            if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                to_list.append('compliance@nordiccreditrating.com')

            header = "{} | the rating job has been finalized".format(
                rating_decision_obj.issuer
            )

            # Send notification
            send_email.delay(header=header,
                             body='If this a public rating, the publishing '
                                  'process will now commence.',
                             to=to_list,
                             from_sender=None,)

            """If there is a previous decision, flag it as non-current."""
            try:
                RatingDecision.objects.filter(
                    pk=rating_decision_obj.previous_rating.pk).update(
                    is_current=False,)
            except AttributeError:
                pass

            rating_decision_obj.is_current = True
            rating_process_obj.process_ended = timezone.now()

            # Create a DecisionAttribute object that
            # summarizes the rating decision
            refresh_decision_attributes(rating_decision_obj)

            # Create decisions on the issue level
            update_issue_rating(rating_decision_obj)

            # Create a draft campaign with MailChimp
            if rating_decision_obj.rating_type.id == 1:
                run_create_campaign.delay(rating_decision_obj.id)

            rating_decision_obj.process_step = 10

        # Save changes
        rating_process_obj.save()
        rating_decision_obj.save()

    redirect_url = request.META.get('HTTP_REFERER', '/') + '#' + hash

    return http.HttpResponseRedirect(redirect_url)


def confirm_parameter(request, pk):
    """Confirm date, chair or member."""

    action = request.GET.get('action')

    if action:

        if action == 'member':

            committee_member_obj = JobMember.objects.get(
                pk=pk)
            committee_member_obj.committee_member_confirmed = True
            committee_member_obj.save()

        return redirect(
            'dashboard')


# pylint: disable=too-many-ancestors
class PressReleaseUpdateView(AjaxUpdateView):
    """PressReleaseUpdateView view."""

    model = PressRelease
    form_class = EditPressReleaseForm
    pk_url_kwarg = 'press_release_pk'

    def get_form_kwargs(self):
        """Custom method for a kwargs to pass to form class."""

        press_release_obj = PressRelease.objects.get(
            id=self.kwargs['press_release_pk'])

        kwargs = super(PressReleaseUpdateView, self).get_form_kwargs()
        kwargs.update(
            {'field': self.kwargs['field'],
             'press_release_obj': press_release_obj}
        )

        return kwargs


class ViewRatingJob(DetailView):
    """View a rating job View."""

    model = RatingDecision
    template_name = 'issuer/rating_job/index_stand_alone.html'
    pk_url_kwarg = 'rating_decision_pk'

    def get_context_data(self, **kwargs):
        """Custom get_context_data method."""

        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        b = return_company_context(self.request,
                                   self.kwargs['pk'],
                                   self.kwargs['rating_decision_pk'],)

        # Merge dicts
        context = {**context, **b}

        return context


# pylint: disable=too-many-ancestors
class IssueRatingDecisionAddView(AjaxCreateView):
    """Add seniority of an issue to the rating decision."""

    model = IssueDecision
    form_class = IssueRatingDecisionAddForm

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):
        kwargs = super(IssueRatingDecisionAddView, self).get_form_kwargs()

        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_valid(self, form):

        obj = form.save(commit=False)

        obj.proposed_by = self.request.user
        obj.issue_id = form.cleaned_data['issue_id']
        obj.is_current = False
        obj.rating_decision_issue_id = form.cleaned_data[
            'rating_decision_issue_id']
        obj.rationale = form.cleaned_data[
            'rationale']

        if form.cleaned_data['ready_for_decision']:
            obj.process_step = 2

            messages.add_message(
                self.request,
                messages.INFO,
                'Sent issue rating decision for final approval.')

        else:

            messages.add_message(
                self.request,
                messages.INFO,
                'Saved issue rating decision.')

        obj.save()

        return super(IssueRatingDecisionAddView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class IssueRatingDecisionEditView(AjaxUpdateView):
    """Add seniority of an issue to the rating decision."""

    model = IssueDecision
    pk_url_kwarg = 'issue_decision_pk'
    form_class = IssueRatingDecisionEditForm

    def get_form_kwargs(self):
        """Custom get_form_kwargs method."""

        kwargs = super(IssueRatingDecisionEditView, self).get_form_kwargs()

        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def get_success_url(self):
        """Custom get_success_url method."""

        return self.request.META.get('HTTP_REFERER')

    def form_valid(self, form):
        """Custom form_valid method."""

        obj = form.save(commit=False)

        # If all is clear for a decision, push the object
        # forward for someone to approve it
        if form.cleaned_data['ready_for_decision']:
            obj.process_step = 2

            messages.add_message(
                self.request,
                messages.INFO,
                'Sent issue rating decision for final approval.')

        elif form.cleaned_data['give_final_approval']:

            # This makes the decision valid and official
            obj.is_current = True

            # set chair = request.user
            obj.chair = self.request.user

            # Finish the process
            obj.process_step = 10

            # Committee timestamp is now
            obj.date_time_committee = timezone.now()

            # Send an email to issuer with the decision
            to_list = [
                obj.issue.issuer.analyst.primary_analyst.email,
            ]

            cc_list = [
                obj.issue.issuer.analyst.primary_analyst.email,
                obj.issue.issuer.analyst.secondary_analyst.email,
                obj.issue.issuer.relationship_manager.email,
            ]

            header = ISSUE_DECISION_HEADER.format(obj.issue.isin)
            body = ISSUE_DECISION_BODY.format(
                obj.get_decided_lt_display(),
                obj.issue.isin,
            )

            # Send notification
            send_email.delay(
                header=header,
                body=body,
                to=to_list,
                cc=cc_list,
            )

            # Set a timestamp when we informed the issuer
            obj.date_time_communicated_issuer = timezone.now()

            # We publish immediately following decision for issues
            obj.date_time_published = timezone.now() + timedelta(seconds=10)

            # Set all the attribute flags
            refresh_issue_decision_attributes(obj,
                                              is_between_committees=True)

            messages.add_message(
                self.request,
                messages.INFO,
                'Final decision for issue confirmed and saved.')

        else:

            messages.add_message(
                self.request,
                messages.INFO,
                'Saved issue rating decision.')

        obj.save()

        return super(IssueRatingDecisionEditView, self).form_valid(form)
