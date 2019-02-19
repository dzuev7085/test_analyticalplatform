# Django
from django.shortcuts import render

from rating_process.models.internal_score_data import InternalScoreData
from rating_process.models.rating_decision import RatingDecision
from issuer.models import Issuer
from pycreditrating import Rating as PCRRating
from rating_process.util import generate_rating_dict


def view_subscore_list(request, issuer_type_pk):
    """View a list of issuers, their latest rating decision and
    respective subscores."""

    output_list = []

    issuers = Issuer.objects.filter(
        rating_decision_issuer__is_current=True,
        issuer_type_id=issuer_type_pk
    ).order_by(
        'gics_sub_industry__industry__industry_group__sector',
        'address__country').select_related(
        'gics_sub_industry__industry__industry_group__sector').\
        select_related('issuer_type').\
        select_related('address__country')

    for i in issuers:
        issuer_data = {}

        issuer_data['current_rating'] = {}

        issuer_data['issuer'] = i

        # Current rating decision
        rating_decision_obj = RatingDecision.objects.select_related(
            'rating_type').\
            get(
            is_current=True,
            issuer=i, )
        issuer_data['current_rating']['data'] = rating_decision_obj

        # Get all subscores
        score_data = InternalScoreData.objects.filter(
            rating_decision__is_current=1,
            rating_decision__issuer=i).select_related(
            'subfactor')

        # All scores
        issuer_data['current_rating']['score_data'] = {}
        for x in score_data:
            issuer_data['current_rating']['score_data'][
                x.subfactor.name] = {
                'score_display':
                    x.get_decided_score_display(),
                'score_value':
                    x.decided_score,
                'weight':
                    x.weight,
                'adjustment_value':
                    x.decided_notch_adjustment, }

        # Calculated rating
        decided_calculated_rating = PCRRating(
            generate_rating_dict(
                i.issuer_type.description,
                score_data,
                'decided'))
        issuer_data['current_rating'][
            'calculated_rating'] = decided_calculated_rating

        output_list.append(issuer_data)

    context = {
        'issuer_list': output_list,
        'issuer_type': issuer_type_pk,
    }

    return render(
        request,
        'sector/index.html',
        context
    )
