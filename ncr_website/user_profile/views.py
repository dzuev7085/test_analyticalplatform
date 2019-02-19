from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from issuer.models import Issuer
from issue.models import Issue

from rating_process.models.rating_decision import RatingDecision
from rating_process.models.job_member import JobMember
from rating_process.models.issue_decision import IssueDecision
from credit_assessment.models.assessment import AssessmentJob


@login_required(login_url='/login/')
def user_dashboard(request):
    """Presents a dashboard to the user."""

    my_issuers = Issuer.objects.filter(analyst__primary_analyst=request.user) \
        | Issuer.objects.filter(
        analyst__secondary_analyst=request.user)

    rating_decision_obj = RatingDecision.objects.in_committee()

    #####################################
    # Where is user part of a rating job?
    #####################################
    am_chair = list(rating_decision_obj.filter(
        chair=request.user))

    committee_member = list(rating_decision_obj.filter(
        jobmember__group_id=1,
        jobmember__member=request.user))

    # Rating jobs
    unconfirmed_members = JobMember.objects.filter(
        member=request.user,
        committee_member_confirmed=False)

    my_committee = (am_chair +
                    committee_member)

    ###########################
    # Chair and action required
    ###########################
    base = RatingDecision.objects.in_progress().filter(
        chair=request.user,
        process_step__in=[2, 8])

    ###########################
    # CRO
    ###########################
    cro = {}
    cro['in_committe'] = rating_decision_obj
    cro['issuers'] = Issuer.objects.is_live()

    #####################################
    # Issue rating decisions
    #####################################
    # We do not permit approving your own proposed decisions
    pending_issue_decision = IssueDecision.objects.filter(
        date_time_deleted__isnull=True,
        process_step=2,
    ).exclude(proposed_by=request.user)

    #####################################
    # Stats
    #####################################
    no_rating = RatingDecision.objects.filter(
        is_current=True,
    )

    no_issue_rating = IssueDecision.objects.filter(
        is_current=True,
        issue__is_matured=False,
    )

    no_corporate_assessment = AssessmentJob.objects.filter(
        is_current=True,
        issuer__issuer_type_id__id__in=[1, 3]
    )

    no_fi_assessment = AssessmentJob.objects.filter(
        is_current=True,
        issuer__issuer_type_id__id__in=[2]
    )

    issues = Issue.objects.filter(is_matured=False).order_by('maturity')[0:10]

    context = {'issuers': my_issuers,
               'my_committee': my_committee,
               'unconfirmed_members': unconfirmed_members,
               'chair_attention_required': base,
               'cro': cro,
               'stats': {
                   'no_rating': len(no_rating),
                   'no_issue_rating': len(no_issue_rating),
                   'no_corporate_assessment': len(no_corporate_assessment),
                   'no_fi_assessment': len(no_fi_assessment),
               },
               'issues': issues,
               'pending_issue_decision': pending_issue_decision, }

    return render(
        request,
        'user/dashboard/index.html',
        context
    )


def change_password(request):
    """Allow the user to change password."""

    if request.method == 'POST':

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request,
                             'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {
        'form': form
    })
