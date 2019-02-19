import os
import csv
import codecs
import datetime
from django.shortcuts import render
from issuer.models import Issuer
from django.urls import reverse_lazy
from pycreditrating import (
    Rating as PCRRating,
    RATING_LONG_TERM,
)
from django.http import HttpResponse
from rating_process.util import generate_rating_dict
from credit_assessment.models.assessment import AssessmentJob
from credit_assessment.models.subscores import AssessmentSubscoreData
from credit_assessment.models.seniority_level_assessment import \
    SeniorityLevelAssessment
from rating_process.models.internal_score_data import InternalScoreData
from a_helper.modal_helper.views import (
    AjaxUpdateView,
    AjaxCreateView
)
from credit_assessment.forms import (
    EditRatingAssessment,
    CreateRatingAssessment,
    EditSubfactorPeer,
    CreateUpdatedAssessment,
)
from rating_process.models.rating_decision_issue import RatingDecisionIssue
from rating_process.models.rating_decision import RatingDecision
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils import timezone
from credit_assessment.utils import get_issues_relative_level
from django.contrib.auth.models import User


def list_assessment(request, type):
    """View a list of issuers, their latest rating decision and
    respective sub scores."""

    output_list = []

    if int(type) == 1:
        include_types = [1, 3]

        template = 'issuer/assessment/list_all_v2.html'

    else:
        include_types = [2]

        template = 'issuer/assessment/list_all_v2.html'

    issuers = Issuer.objects.list_all_assessment(
        include_types
    )

    # Create a dict of all users to reduce db hits
    user_dict = {}
    users = User.objects.all()
    for u in users:
        user_dict[u.id] = {
            'short_name': u.first_name[:1] + u.last_name[:1],
            'name': u.first_name + ' ' + u.last_name
        }

    #####################################################
    # Authentication
    #####################################################
    group_list = request.user.groups.all().values('name')
    user_groups = []
    for group in group_list:
        user_groups.append(group['name'])

    for i in issuers:
        # Create dict to store data for this issuer
        issuer_data = {}

        # Version for the dict sent to pycreditrating
        version = 2

        # Store information about the issuer
        issuer_data['issuer'] = i

        issuer_data['user_data'] = {}
        issuer_data['user_data'] = user_dict[i.initiated_by]

        if i.rating_id:

            score_data = InternalScoreData.objects.filter(
                rating_decision_id=i.rating_id,
            ).select_related('subfactor')

        elif i.progress_id:

            score_data = AssessmentSubscoreData.objects.filter(
                assessment_id=i.progress_id,
            ).select_related('subfactor').\
                select_related('assessment__highestlowest')

        else:

            score_data = AssessmentSubscoreData.objects.filter(
                assessment_id=i.current_id,
            ).select_related('subfactor').\
                select_related('assessment__highestlowest')

        # All scores
        issuer_data['score_data'] = {}
        for x in score_data:

            # For backwards compatibility
            if x.subfactor.id == 5:
                version = 1

            issuer_data['score_data'][
                x.subfactor.name] = {
                'score_display':
                    x.get_decided_score_display(),
                'score_value':
                    x.decided_score,
                'weight':
                    x.weight,
                'adjustment_value':
                    x.decided_notch_adjustment,
                'subfactor':
                    x.subfactor.name,
                'id':
                    x.id, }

        # Calculated rating
        calculated_rating = PCRRating(
            generate_rating_dict(
                i.i_id,
                score_data,
                'decided',
                version=version,
            )
        )

        issuer_data['calculated_rating'] = calculated_rating

        # Ratings per issuer seniority level
        if i.rating_id:

            seniority_level = RatingDecisionIssue.objects.filter(
                rating_decision_id=i.rating_id,
            ).select_related('seniority')

        elif i.progress_id:
            seniority_level = SeniorityLevelAssessment.objects.filter(
                assessment_id=i.progress_id,
            ).select_related('seniority')

        else:
            seniority_level = SeniorityLevelAssessment.objects.filter(
                assessment_id=i.current_id,
            ).select_related('seniority')

        issuer_data['seniority_level'] = {}
        for x in seniority_level:

            try:
                relative_notch = RATING_LONG_TERM[
                                     calculated_rating.issuer_rating] - \
                                 x.decided_lt
            except (TypeError, KeyError):

                relative_notch = 'n/a'

            issuer_data['seniority_level'][
                x.seniority.name] = {
                'relative_score':
                    relative_notch,
                'score_display':
                    x.get_decided_lt_display()
            }

        # The user that created the assessment must not be allowed to
        # edit the assessment
        issuer_data['misc'] = {}

        # If the assessment is in final approval phase, we want to make sure
        # the approval is not made by the same user that initiated the
        # assessment
        if i.progress_process_step == 2:

            if request.user.id == i.progress_initiated_by_id:
                issuer_data['misc']['allow_edit'] = False
            else:
                issuer_data['misc']['allow_edit'] = True
        else:

            # There is no assessment in progress, while one was made
            # in the past
            if i.current_id and not i.progress_id:
                issuer_data['misc']['allow_edit'] = False

            else:

                if i.rating_id:
                    issuer_data['misc']['allow_edit'] = False

                else:
                    issuer_data['misc']['allow_edit'] = True

        if 'Analyst' not in user_groups:
            issuer_data['misc']['allow_edit'] = False

        output_list.append(issuer_data)

    context = {
        'object_list': output_list,
        'type': int(type),
    }

    return render(
        request,
        template,
        context
    )


# pylint: disable=too-many-ancestors
class AssessmentUpdateView(AjaxUpdateView):
    """AssessmentUpdateView view."""

    model = AssessmentJob
    pk_url_kwarg = 'assessment_pk'
    form_class = EditRatingAssessment

    def get_form_kwargs(self):
        """Custom get_form_kwargs."""

        kwargs = super(AssessmentUpdateView, self).get_form_kwargs()
        kwargs.update({'assessment_pk': self.kwargs['assessment_pk']})

        return kwargs

    def form_valid(self, form):
        """Custom form_valid method."""

        d = form.save(commit=False)

        issue_seniority_lvl = {}

        for key, value in sorted(form.cleaned_data.items()):
            try:
                a = key.split('_')[0]
                b = key.split('_')[1]

                if a == 'i':

                    issue_seniority_lvl[int(b)] = int(value)

                else:

                    obj = AssessmentSubscoreData.objects.get(pk=b)

                    if a == 's':
                        # n/a is represented as empty value
                        if value == '':
                            value = None

                        obj.decided_score = value

                    elif a == 'n':
                        obj.decided_notch_adjustment = value

                    elif a == 'w':
                        # 0% is represented as empty value
                        if value == '':
                            value = None

                        obj.weight = value

                    obj.save()

            except (IndexError, ValueError):
                pass

        try:
            internal_score_obj = AssessmentSubscoreData.objects.filter(
                assessment_id=self.kwargs['assessment_pk']
            ).all()

            # Issuer type id is used to create the rating below
            issuer_type_id = d.issuer.issuer_type.id

            # Return indicative ratings based on score input
            proposed_rating = PCRRating(generate_rating_dict(
                issuer_type_id,
                internal_score_obj,
                'decided',
                version=2)
            )

            ass = RATING_LONG_TERM[proposed_rating.issuer_rating]

            d.assessment_lt = ass

        except Exception:

            d.assessment_lt = None

        try:
            # Save issue level assessments
            i_lvl = SeniorityLevelAssessment.objects.filter(
                assessment_id=self.kwargs['assessment_pk'],
            )

            for i in i_lvl:

                try:
                    # The assessments are stored relative to the issuer
                    # assessment

                    i.decided_lt = d.assessment_lt - issue_seniority_lvl[i.id]
                    i.save()

                except ValueError:
                    pass

        except Exception:
            pass

        if form.cleaned_data['ready_for_approval']:
            # The user has marked the assessment as ready for approval,
            # flag it as such

            d.process_step = 2
            d.initiated_by = self.request.user

            messages.add_message(
                self.request,
                messages.INFO,
                'The assessment has been flagged as ready for approval.')

        elif form.cleaned_data['give_final_approval']:

            # Mark all previous assessment for issuer as non-current
            AssessmentJob.objects.filter(
                issuer=d.issuer
            ).update(
                is_current=False
            )

            # This makes the decision valid and official
            d.is_current = True

            # Finish the process
            d.process_step = 10

            # Committee timestamp is now
            d.date_time_approval = timezone.now()

            messages.add_message(
                self.request,
                messages.INFO,
                'Assessment approved and saved to database.')

        else:

            messages.add_message(
                self.request,
                messages.INFO,
                'Saved assessment.')

        d.save()

        return super(AssessmentUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class AssessmentCreateView(SuccessMessageMixin, AjaxCreateView):
    """AssessmentCreateView view."""

    model = AssessmentJob
    success_url = reverse_lazy('issuer_assessment_corporate_all')
    success_message = "Setting up of credit assessment for %(legal_name)s " \
                      "was sucessful"

    form_class = CreateRatingAssessment

    def get_success_message(self, cleaned_data):
        """Custom get_success_message method."""

        return self.success_message % dict(
            cleaned_data,
            legal_name=self.object.issuer.legal_name,
        )

    def form_valid(self, form):
        """Custom form_valid method."""

        d = form.save(commit=False)

        d.initiated_by = self.request.user

        d.save()

        return super(AssessmentCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class AssessmentCreateUpdateView(SuccessMessageMixin, AjaxCreateView):
    """AssessmentCreateUpdateView view."""

    model = AssessmentJob
    success_url = reverse_lazy('issuer_assessment_corporate_all')
    success_message = "Created a credit assessment for %(legal_name)s"

    form_class = CreateUpdatedAssessment

    def get_form_kwargs(self):
        """Custom get_form_kwargs."""

        kwargs = super(AssessmentCreateUpdateView, self).get_form_kwargs()
        kwargs.update({'issuer_pk': self.kwargs['issuer_pk']})

        return kwargs

    def get_success_message(self, cleaned_data):
        """Custom get_success_message method."""

        return self.success_message % dict(
            cleaned_data,
            legal_name=self.object.issuer.legal_name,
        )

    def form_valid(self, form):
        """Custom form_valid method."""

        d = form.save(commit=False)

        d.initiated_by = self.request.user

        d.save()

        return super(AssessmentCreateUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class EditSubfactorPeerView(AjaxUpdateView):
    """AssessmentUpdateView view."""

    model = AssessmentSubscoreData
    pk_url_kwarg = 'subfactor_id'
    form_class = EditSubfactorPeer

    def get_form_kwargs(self):
        """Custom get_form_kwargs."""

        kwargs = super(EditSubfactorPeerView, self).get_form_kwargs()
        kwargs.update({'subfactor_id': self.kwargs['subfactor_id']})
        kwargs.update({'user': self.request.user})

        return kwargs

    def form_valid(self, form):
        """Custom form_valid method."""

        # Save the score immediately so it's available below
        obj = form.save(commit=False)
        obj.save()

        subscore_data_list = []

        for key, value in sorted(form.cleaned_data.items()):

            try:
                a = key.split('_')[0]
                b = key.split('_')[1]

                obj = AssessmentSubscoreData.objects.get(pk=b)
                subscore_data_list.append(obj.assessment.id)

                if a == 's':
                    # n/a is represented as empty value
                    if value == '':
                        value = None

                    obj.decided_score = value

                elif a == 'n':
                    obj.decided_notch_adjustment = value

                elif a == 'w':
                    # 0% is represented as empty value
                    if value == '':
                        value = None

                    obj.weight = value

                obj.save()

            except (IndexError, ValueError):
                pass

        # Loop through all subscores that were affected by the change
        # and update the calculated rating for each

        # Add the clicked issuer subscore to the list to loop through
        subscore_data_list.append(form.instance.assessment.id)
        for d in AssessmentJob.objects.filter(id__in=subscore_data_list):

            # Store the current assessment level, as we need to get the
            # relative value of each issue level
            # Has to be initialized here, before the rating is updated
            issue_assessment_dict = get_issues_relative_level(d)

            internal_score_obj = AssessmentSubscoreData.objects.filter(
                assessment_id=d.id
            ).all()

            try:

                # Issuer type id is used to create the rating below
                issuer_type_id = d.issuer.issuer_type.id

                # Return indicative ratings based on score input
                proposed_rating = PCRRating(generate_rating_dict(
                    issuer_type_id,
                    internal_score_obj,
                    'decided',
                    version=2)
                )

                # Assign and save the assessment
                d.assessment_lt = RATING_LONG_TERM[
                    proposed_rating.issuer_rating]

                for key in issue_assessment_dict:

                    v = SeniorityLevelAssessment.objects.get(pk=key)
                    v.decided_lt = d.assessment_lt - issue_assessment_dict[key]
                    v.save()

            except Exception:

                d.assessment_lt = None

            d.save()

        messages.add_message(
            self.request,
            messages.INFO,
            'Saved sub factor assessments.')

        return super(EditSubfactorPeerView, self).form_valid(form)


def export_users_csv(request):
    """Export all current assessments as Excel"""

    file_name = 'assessment_csv_{}.csv'.format(
        datetime.datetime.now().strftime('%Y-%m-%d')
    )

    with codecs.open(file_name, "w", encoding='utf-8') as fp:

        writer = csv.writer(
            fp,
            delimiter=';'
        )

        writer.writerow(['Peer group', 'Issuer', 'LEI', 'Assessment',
                         'Approval date', 'Senior Secured', 'Senior Unsecured',
                         'Senior non-preferred', 'Subordinated', 'Tier 2',
                         'AT1'])

        issuers = Issuer.objects.list_all_assessment([1, 2, 3])

        for i in issuers:

            senior_secured = None
            senior_unsecured = None
            senior_npf = None
            subordinated = None
            tier2 = None
            at1 = None

            # Issuer has a rating, fetch it
            if i.rating_id:
                d = RatingDecision.objects.get(pk=i.rating_id)

                # Get all decisions for seniority levels
                seniority_lvl = RatingDecisionIssue.objects.filter(
                    rating_decision=d,
                )

                try:
                    senior_secured = seniority_lvl.get(
                        seniority_id=2).get_decided_lt_display()
                except RatingDecisionIssue.DoesNotExist:
                    pass

                try:
                    senior_unsecured = seniority_lvl.get(
                        seniority_id=1).get_decided_lt_display()
                except RatingDecisionIssue.DoesNotExist:
                    pass

                try:
                    subordinated = seniority_lvl.get(
                        seniority_id=4).get_decided_lt_display()
                except RatingDecisionIssue.DoesNotExist:
                    pass

                try:
                    tier2 = seniority_lvl.get(
                        seniority_id=4).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    senior_npf = seniority_lvl.get(
                        seniority_id=5).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    at1 = seniority_lvl.get(
                        seniority_id=3).get_decided_lt_display()
                except Exception:
                    pass

                if d.issuer.issuer_type.id == 2:
                    subordinated = None
                else:
                    tier2 = None

                data = (
                    i.internal_peer,
                    i.legal_name,
                    i.lei,

                    d.get_decided_lt_display(),
                    d.date_time_published.strftime('%Y-%m-%d'),

                    senior_secured,
                    senior_unsecured,
                    senior_npf,
                    subordinated,
                    tier2,
                    at1,
                )

            else:
                d = AssessmentJob.objects.get(pk=i.current_id)

                # Get all decisions for seniority levels
                seniority_lvl = SeniorityLevelAssessment.objects.filter(
                    assessment=d,
                )

                try:
                    senior_secured = seniority_lvl.get(
                        seniority_id=2).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    senior_unsecured = seniority_lvl.get(
                        seniority_id=1).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    subordinated = seniority_lvl.get(
                        seniority_id=4).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    tier2 = seniority_lvl.get(
                        seniority_id=4).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    senior_npf = seniority_lvl.get(
                        seniority_id=5).get_decided_lt_display()
                except Exception:
                    pass

                try:
                    at1 = seniority_lvl.get(
                        seniority_id=3).get_decided_lt_display()
                except Exception:
                    pass

                if d.issuer.issuer_type.id == 2:
                    subordinated = None
                else:
                    tier2 = None

                data = (
                    i.internal_peer,
                    i.legal_name,
                    i.lei,

                    d.get_assessment_lt_display(),
                    d.date_time_approval.strftime('%Y-%m-%d'),

                    senior_secured,
                    senior_unsecured,
                    senior_npf,
                    subordinated,
                    tier2,
                    at1,
                )

            # Replace the assessment sort order with its character value
            writer.writerow(data)

    with codecs.open(file_name, 'r', encoding='utf-8') as fh:
        response = HttpResponse(fh, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            file_name
        )

        os.remove(file_name)

        return response
