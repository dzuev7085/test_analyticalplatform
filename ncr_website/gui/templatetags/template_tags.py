""""Template tags."""
import base64
import os

from django import template
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.conf import settings

from pycreditrating import (
    Rating as PCRRating,
    RATING_LONG_TERM_OUTLOOK_REVERSE,
    RATING_LONG_TERM_REVERSE,
    RATING_SHORT_TERM
)

from rating_process.util import generate_rating_dict

from a_helper.static_database_table.models.country import CountryRegion
from a_helper.static_database_table.models.gics import GICSSector

from rating_process.models.internal_score_data import (
    InternalScoreData,
)

from rating_process.models.rating_decision import RatingDecision
from rating_process.models.rating_decision_issue import RatingDecisionIssue
from rating_process.models.job_member import JobMember
from rating_process.const import PHASES_HUMAN_READABLE

from issuer.models import Issuer

from upload.models import AnalyticalDocument

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return a value from a dictionary."""

    return dictionary.get(key)


@register.filter
def in_list(list, key):
    """Return a value from a dictionary."""

    if key in list:
        return True
    else:
        return False


@register.filter(name='format_plus_minus')
def format_plus_minus(value):
    """Return value including +/-."""
    try:
        if value >= 0:
            return '+' + str(value)
        else:
            return value
    except:  # noqa E722
        return '+0'


@register.filter(name='format_percent')
def format_percent(value, decimals=0):
    """Return value including %."""

    if value:
        return format(value, "." + str(decimals) + "%")


@register.filter(name='format_mn')
def format_mn(value, decimals=0):
    """Return value including mn."""

    if value is not None and value != 0:
        o = round(value / 1000000, decimals)

    else:
        # Return a nbsp to make cells clickable.
        o = '&nbsp;'

    return mark_safe(o)


@register.simple_tag
def active(request, pattern):
    """Check if pattern exists in path."""
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''


@register.simple_tag
def format_reference_number(prefix=None, number=None, object_type=None):
    """Format number and prepend six digits."""

    if object_type == 'rating_scale':
        reference_number = 'RS' + str(number).zfill(6)

    elif object_type == 'debt_class':
        reference_number = 'DC' + str(number).zfill(6)

    elif object_type == 'issue_program':
        reference_number = 'IP' + str(number).zfill(6)

    elif object_type == 'rating_type':
        reference_number = 'RT' + str(number).zfill(6)

    elif object_type == 'rating_scope':
        """Only used for ESMA validation."""
        reference_number = 'RSc' + str(number).zfill(6)

    elif object_type == 'rating_category':
        """Only used for ESMA validation."""
        reference_number = 'RCa' + str(number).zfill(6)

    elif object_type == 'rating_notch':
        """Only used for ESMA validation."""

        reference_number = 'RNo' + str(number).zfill(6)
    elif object_type == 'cra_info':
        """Only used for ESMA validation."""

        reference_number = 'CRA' + str(number).zfill(6)

    elif object_type == 'rating_decision':
        reference_number = 'R' + str(number).zfill(12)

    elif object_type == 'issuer':
        reference_number = 'I' + str(number).zfill(6)

    elif object_type == 'issue':
        reference_number = 'IU' + str(number).zfill(12)

    elif object_type == 'rating_action':
        reference_number = 'RA' + str(number).zfill(38)

    else:
        reference_number = prefix.upper() + str(number).zfill(10)

    return reference_number


@register.filter(name='return_long_term_rating')
def return_long_term_rating(value, default='NR'):
    """Return long-term rating as letters."""
    try:
        return RATING_LONG_TERM_REVERSE[value]
    except KeyError:
        return default


@register.filter(name='return_long_term_rating_outlook')
def return_long_term_rating_outlook(value, default='NR'):
    """Return long-term rating test."""
    try:
        return RATING_LONG_TERM_OUTLOOK_REVERSE[value]
    except KeyError:
        return default


@register.filter(name='return_short_term_rating')
def return_short_term_rating(value, default='NR'):
    """Return short-term rating as letters."""
    try:
        return RATING_SHORT_TERM[value]
    except KeyError:
        return default


@register.filter(name='gics_sector')
def return_gics_sector(sub_industry):
    """Return a readable, top-level, GICS-name."""
    try:
        return GICSSector.objects.get(
            sector=int(str(sub_industry)[:2])).sector_name
    except ValueError:
        return None


@register.filter(name='country_name')
def return_country_name(iso_31661_alpha_2):
    """Return a readable (long) country name."""
    return CountryRegion.objects.get(iso_31661_alpha_2=iso_31661_alpha_2).name


@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user is in group."""
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()


@register.simple_tag
def current_rating(issuer, is_bloomberg=False):
    """Return that rating that is currently in effect for an issuer."""

    try:
        rating_decision = RatingDecision.objects.current_rating(issuer)

    except RatingDecision.DoesNotExist:
        rating_decision = False

    # Only return data if the current rating is public
    if rating_decision and rating_decision.rating_type.id in [2, 3]:
        if is_bloomberg:
            return False
        else:
            return rating_decision
    else:
        return rating_decision


@register.simple_tag
def previous_rating(issuer, is_bloomberg=False):
    """Return the rating that was assigned before the most recent
    decision."""

    try:
        r = current_rating(issuer, is_bloomberg).previous_rating
    except (RatingDecision.DoesNotExist, AttributeError):
        r = False

    return r


@register.simple_tag
def existing_score(issuer, subfactor):
    """Return that rating that is currently in effect for an issuer.

    Currently used in sector overview."""

    try:
        existing_decision_obj = current_rating(issuer)

        return InternalScoreData.objects.filter(
            subfactor=subfactor,
            rating_decision=existing_decision_obj
        )[0]

    except:  # noqa E722
        pass


@register.simple_tag
def existing_issue_rating(seniority, existing_decision_obj=None):
    """Return what rating that is currently in effect for an issue."""

    try:
        return RatingDecisionIssue.objects.get(
            rating_decision=existing_decision_obj,
            seniority=seniority
        )

    except:  # noqa E722
        pass


@register.simple_tag
def calculated_rating(issuer_type_id, rating_decision_obj):
    """Calculate the rating based on scores using pycreditrating."""

    internal_score_obj = InternalScoreData.objects.filter(
        rating_decision=rating_decision_obj
    ).all()

    return PCRRating(generate_rating_dict(
        int(issuer_type_id),
        internal_score_obj,
        'decided'),)


@register.simple_tag
def recommended_or_decided(rating_decision_obj):
    """Indicate whether the decision is a recommendation or decided."""

    if rating_decision_obj.get_process_step_display() == 'analytical_phase':
        return 0
    else:
        return 1


@register.simple_tag
def recommended_or_decided_outlook(rating_decision_obj):
    """Return the name of the outlook field to be updated."""

    if rating_decision_obj.get_process_step_display() == 'analytical_phase':
        return 'proposed_lt_outlook'
    else:
        return 'decided_lt_outlook'


@register.simple_tag
def recommended_or_decided_st(rating_decision_obj):
    """Return the name of the short-term rating field to be updated."""

    if rating_decision_obj.get_process_step_display() == 'analytical_phase':
        return 'proposed_st'
    else:
        return 'decided_st'


@register.simple_tag
def rating_process_document_id(rating_decision_pk, document_type_pk):
    """Return the object for an analytical document."""

    try:
        return AnalyticalDocument.objects.select_related(
            'rating_decision').select_related(
            'document_type').values_list('id', flat=True).get(
            rating_decision__pk=rating_decision_pk,
            document_type__pk=document_type_pk)

    except AnalyticalDocument.DoesNotExist:
        return None


@register.simple_tag
def rating_process_phase(issuer_obj):
    """Where are we in the rating process?"""

    try:

        key = RatingDecision.objects.in_progress().get(
            issuer=issuer_obj).get_process_step_display()

    except RatingDecision.DoesNotExist:

        rating_history = RatingDecision.objects.valid_decisions().filter(
            issuer=issuer_obj)

        if len(rating_history) > 0:
            """Rating decisions have been made in the past."""

            key = 'surveillance'
        else:
            key = 'not_started'

    return PHASES_HUMAN_READABLE[key]


@register.simple_tag
def rating_job_role(rating_decision_obj, user):
    """Returns what role a user has in a committees"""

    role = None

    try:

        RatingDecision.objects.get(id=rating_decision_obj.id,
                                   chair_id=user)
        role = 'Chair'

    except RatingDecision.DoesNotExist:

        try:
            job_member_obj = JobMember.objects.filter(
                rating_decision=rating_decision_obj,
                member_id=user)[0]

            if job_member_obj.role.id == 1:
                role = 'Voter'
            elif job_member_obj.role.id == 2:
                role = 'Observer'

        except JobMember.DoesNotExist:

            issuer = Issuer.objects.get(
                pk=rating_decision_obj.issuer.id)

            if issuer.analyst.primary_analyst == user:
                role = 'Primary analyst'
            elif issuer.analyst.secondary_analyst == user:
                role = 'Secondary analyst'

    return role


@register.simple_tag
def bool2int(bool):
    """Converts bool to int"""

    return int(bool)


@register.filter(name='strip_p_tag')
def strip_p_tag(string):
    """Strip beginning and ending <p> from string."""

    try:
        return string[3:-4]
    except TypeError:
        return ''


@register.simple_tag
def get_subscore(dictionary, key, subkey):
    """Get a formatted score for a rating subfactor."""

    try:
        return dictionary[key][subkey]
    except KeyError:
        return 'n/a'


@register.simple_tag
def static_file2base64(file, tmp=False):
    """Convert an image in the static folder to base64."""

    if tmp:
        file = settings.BASE_DIR + '/tmp/' + file
    else:
        if os.environ['ENVIRONMENT_MODE'] == 'DEV':
            file = settings.BASE_DIR + '/static/' + file
        else:
            file = ('/var/www/' +
                    os.environ['ENVIRONMENT_MODE'] + '/static/' + file)

    with open(file, "rb") as imageFile:
        x = base64.b64encode(imageFile.read())

    # Return the string as a string and marked safe for Django
    return mark_safe(x.decode("utf-8"))


@register.simple_tag
def static_file2string(file):
    """Return any static file as a string."""

    if os.environ['ENVIRONMENT_MODE'] == 'DEV':
        file = settings.BASE_DIR + '/static/' + file
    else:
        file = ('/var/www/' +
                os.environ['ENVIRONMENT_MODE'] + '/static/' + file)

    with open(file, "rb") as output_file:
        x = output_file.read()

    # Return the string as a string and marked safe for Django
    return mark_safe(x.decode("utf-8"))
