"""Module to load rating decision data to be sent to ESMA."""
from datetime import timedelta

from celery.utils.log import get_task_logger

from rating_process.models.rating_decision import RatingDecision
from rating_process.models.issue_decision import IssueDecision

from integrations.esma.utils.populate_rating_decision.create_objects import (
    create_rating_decision_xml_objects
)

from integrations.esma.utils.hash_functions import create_hash

from integrations.esma.models.qt_rating_action import (
    QTRatingCreateData,
)

from gui.templatetags.template_tags import format_reference_number

from integrations.esma.const import ACTION_TYPE
from integrations.esma.utils.mapping_functions import get_outlook_trend
from integrations.esma.utils.populate_rating_decision.helpers import (
    get_attributes,
)

logger = get_task_logger(__name__)


def populate_rating_decision(issues=False):
    """Check today's decisions."""

    # Check if the decision has been sent already
    # Ordering is important!
    # there is a constant in CONST defining how long to look back
    if issues:
        decision_backlog = IssueDecision.objects.esma()

    else:
        decision_backlog = RatingDecision.objects.esma()

    if issues:
        # Only the long-term perspective is relevant for issues
        PERSPECTIVES = [
            1,  # Long-term
        ]

    else:
        PERSPECTIVES = [
            1,  # Long-term
            2,  # Short-term
        ]

    # Loop through each record from the past n days
    for x in decision_backlog:

        logger.info("   analyzing decision: " + str(x))

        # Pick up the decision attributes
        attributes = get_attributes(issues, x)

        # Reset the values
        iss = None

        debt_classification_code = None
        issuer_rating_type_code = None

        # Store previous rating decision, if available
        try:
            previous_rating = x.previous_rating
        except Exception:
            previous_rating = False

        if issues:
            # Issue instance
            iss = x

            # Rating decision instance
            dec = x.rating_decision_issue.rating_decision
        else:

            # Rating decision instance
            dec = x

        # Assume there is no previous rating
        prev_rating_preliminary = False

        if issues:
            rated_object = 2  # 2 = Issue

            # Should be seniority
            debt_classification_code = format_reference_number(
                number=iss.issue.seniority.id,
                object_type='debt_class')

        else:
            rated_object = 1  # 1 = Issuer
            issuer_rating_type_code = format_reference_number(
                number=1,
                object_type='rating_type')

        # 2 is financial institution
        if dec.issuer.issuer_type.id == 2:
            industry = 1
        else:
            industry = 3

        # Public rating not exclusively
        # produced for and disclosed
        # to investors for a fee
        if dec.rating_type.id == 1:
            type_of_rating_for_erp = 1
        else:
            type_of_rating_for_erp = 2

        # Logic as provided by ESMA during a call
        # Preliminary issuer ratings and issue ratings should not have
        # this flag
        if dec.decisionattributes.is_new_preliminary or rated_object != 1:
            relevant_for_cerep = False
        else:
            relevant_for_cerep = True

        # Loop through long-term and short-term
        for perspective in PERSPECTIVES:

            logger.info("       perspective: " + str(perspective))

            # There's some unknown error going on
            # try to catch it
            try:

                TEMP = {}
                TEMP_L = {}
                action_type_list = []

                # TODO: not implemented
                # Default these values to NULL in db
                owsd_status = None
                outlook_trend = None
                watch_review = None
                withdrawal_reason_type = None

                ############################################
                # MISC VARIABLES
                ############################################
                if perspective == 1:  # Long-term
                    rating_value = x.decided_lt
                else:
                    rating_value = x.decided_st

                ############################################
                # NEW PRELIMINARY RATING
                ############################################
                # We have to create a new preliminary rating
                # and place an outlook

                if attributes.is_new_preliminary:
                    action_type_list.append(2)

                    # Place an outlook for long-term ratings
                    # Issues dont have outlooks
                    if perspective == 1 and not issues:
                        action_type_list.append(10)

                        TEMP[dec.id] = {
                            10: {
                                'owsd_status': 1,  # place
                                'outlook_trend': get_outlook_trend(dec),
                                'validity_date':
                                    x.date_time_published +
                                    timedelta(minutes=1),
                            }
                        }

                ############################################
                # NEW RATING
                ############################################
                # We have to create a new rating and place
                # an outlook
                elif attributes.is_new:
                    action_type_list.append(3)

                    # Place an outlook for long-term ratings
                    # Issues dont have outlooks
                    if perspective == 1 and not issues:
                        action_type_list.append(10)

                        TEMP[dec.id] = {
                            10: {
                                'owsd_status': 1,  # place
                                'outlook_trend': get_outlook_trend(dec),
                                'validity_date':
                                    x.date_time_published +
                                    timedelta(minutes=1),
                            }
                        }

                    """Check if previous rating was preliminary."""
                    try:
                        if issues:
                            if iss.previous_rating.issuedecisionattributes. \
                                    is_new_preliminary:
                                    prev_rating_preliminary = True
                        else:
                            if dec.previous_rating.decisionattributes. \
                                    is_new_preliminary:
                                    prev_rating_preliminary = True

                    except AttributeError:
                        pass

                ############################################
                # RATING SCALES
                ############################################
                if attributes.is_new_preliminary:
                    if perspective == 1:
                        # Scale for long-term ratings
                        rating_scale_id = 3

                    else:
                        # Scale for short-term ratings
                        rating_scale_id = 4

                else:
                    if perspective == 1:

                        # Scale for long-term ratings
                        rating_scale_id = 1
                    else:

                        # Scale for short-term ratings
                        rating_scale_id = 2

                ############################################
                # LONG-TERM UPGRADED
                ############################################
                if attributes.is_lt_upgrade and perspective == 1:
                    action_type_list.append(4)

                ############################################
                # LONG-TERM DOWNGRADED
                ############################################
                if attributes.is_lt_downgrade and perspective == 1:
                    action_type_list.append(5)

                ############################################
                # LONG-TERM AFFIRMED
                ############################################
                if attributes.is_lt_affirmation and perspective == 1:
                    action_type_list.append(6)

                ############################################
                # SHORT-TERM UPGRADED
                ############################################
                # Not valid for issue ratings, hence the
                # try/catch
                try:
                    if attributes.is_st_upgrade and perspective == 2:
                        action_type_list.append(4)
                except AttributeError:
                    pass

                ############################################
                # SHORT-TERM DOWNGRADED
                ############################################
                # Not valid for issue ratings, hence the
                # try/catch
                try:
                    if attributes.is_st_downgrade and perspective == 2:
                        action_type_list.append(5)

                except AttributeError:
                    pass

                ############################################
                # SHORT-TERM AFFIRMED
                ############################################
                # Not valid for issue ratings, hence the
                # try/catch
                try:
                    if attributes.is_st_affirmation and perspective == 2:
                        action_type_list.append(6)
                except AttributeError:
                    pass

                ############################################
                # DEFAULTS
                ############################################
                # Regular default
                if attributes.is_default:
                    action_type_list.append(7)

                if attributes.is_default:
                    default_flag = True
                else:
                    default_flag = False

                # Selective default
                if attributes.is_selective_default:
                    action_type_list.append(7)

                ############################################
                # RATING SUSPENDED
                ############################################
                if attributes.is_suspension:
                    action_type_list.append(8)

                ############################################
                # RATING WITHDRAWN
                ############################################
                # Note from ESMA: don't withdraw preliminary
                # ratings
                if attributes.is_withdrawal:

                    action_type_list.append(9)

                    try:
                        if attributes.is_matured:
                            TEMP[dec.id] = {
                                9: {
                                    'action_type': 9,
                                    'withdrawal_reason_type': 4,
                                }
                            }

                    except AttributeError:
                        pass

                ############################################
                # RATING OUTLOOK CHANGED
                ############################################
                # Outlook has changed
                # Only check this for long-term perspective
                # According to ESMA you first place an outlook
                # Then you remove the old outlook and place a new one
                try:
                    # 1 = long-term and only for issuer ratings
                    if perspective == 1 and not issues:

                        if attributes.is_outlook_change:

                            # Remove current outlook
                            # Place outlook
                            action_type_list.append(10)
                            action_type_list.append(10)

                            TEMP_L[dec.id] = {
                                10: [
                                    {
                                        'owsd_status': 3,  # remove
                                        'outlook_trend': get_outlook_trend(
                                            previous_rating),
                                        'is_parsed': False,
                                    },
                                    {
                                        'owsd_status': 1,  # Place
                                        'outlook_trend':
                                            get_outlook_trend(dec),
                                        'is_parsed': False,
                                    }
                                ]
                            }

                        # Place a maintain
                        # But not on a new rating
                        elif not attributes.is_new and not \
                                attributes.is_new_preliminary:

                            # Maintain current outlook
                            action_type_list.append(10)
                            TEMP[dec.id] = {
                                10: {
                                    'owsd_status':
                                        2,  # Maintain
                                    'outlook_trend':
                                        get_outlook_trend(dec),
                                }
                            }

                except AttributeError:
                    pass

                ############################################
                # RATING WATCH
                ############################################
                try:
                    if attributes.is_watch:
                        # TODO: implement OSWD_status
                        action_type_list.append(11)

                except AttributeError:
                    pass

            except Exception as e:
                logger.info("Error: " + str(e))

            # Run through all action types from above
            for t in action_type_list:

                logger.info("           action type: " + str(ACTION_TYPE[t]))

                # Defined as list to make sure order is maintained
                hash_input = [x.date_time_published.strftime('%Y-%m-%d'),
                              x.id,
                              t,
                              perspective]
                hash_key = create_hash(*hash_input)

                # A list of action types has been sent,
                # TODO: this is not pretty, but I'm out of time
                try:

                    if type(TEMP_L[dec.id][t]) == list:

                        if not TEMP_L[dec.id][t][0]['is_parsed']:
                            try:
                                owsd_status = TEMP_L[dec.id][t][0][
                                    'owsd_status']
                            except KeyError:
                                pass

                            try:
                                outlook_trend = TEMP_L[dec.id][t][0][
                                    'outlook_trend']
                            except KeyError:
                                pass

                            try:
                                watch_review = TEMP_L[dec.id][t][0][
                                    'watch_review']
                            except KeyError:
                                pass

                            try:
                                withdrawal_reason_type = TEMP_L[dec.id][t][0][
                                    'withdrawal_reason_type']
                            except KeyError:
                                pass

                            try:
                                validity_date = TEMP_L[dec.id][t][0][
                                    'validity_date']
                            except KeyError:
                                # Standard time used in reporting
                                # There is a special case to report outlooks
                                # on new ratings as informed in an email
                                # from ESMA on 2018-10-31, 14.43 with the
                                # validity datetime of the OT action later than
                                # the NW action (e.g. 1 minute later validity
                                # datetime).

                                validity_date = x.date_time_published

                            TEMP_L[dec.id][t][0]['is_parsed'] = True

                        elif not TEMP_L[dec.id][t][1]['is_parsed']:

                            try:
                                owsd_status = TEMP_L[dec.id][t][1][
                                    'owsd_status']
                            except KeyError:
                                pass

                            try:
                                outlook_trend = TEMP_L[dec.id][t][1][
                                    'outlook_trend']
                            except KeyError:
                                pass

                            try:
                                watch_review = TEMP_L[dec.id][t][1][
                                    'watch_review']
                            except KeyError:
                                pass

                            try:
                                withdrawal_reason_type = TEMP_L[dec.id][t][1][
                                    'withdrawal_reason_type']
                            except KeyError:
                                pass

                            try:
                                validity_date = TEMP_L[dec.id][t][1][
                                    'validity_date']
                            except KeyError:
                                # Standard time used in reporting
                                # There is a special case to report outlooks
                                # on new ratings as informed in an email
                                # from ESMA on 2018-10-31, 14.43 with the
                                # validity datetime of the OT action later
                                # than the NW action (e.g. 1 minute later
                                # validity datetime).

                                validity_date = x.date_time_published

                            TEMP_L[dec.id][t][1]['is_parsed'] = True

                    else:

                        try:
                            owsd_status = TEMP[dec.id][t]['owsd_status']
                        except KeyError:
                            pass

                        try:
                            outlook_trend = TEMP[dec.id][t]['outlook_trend']
                        except KeyError:
                            pass

                        try:
                            watch_review = TEMP[dec.id][t]['watch_review']
                        except KeyError:
                            pass

                        try:
                            withdrawal_reason_type = TEMP[dec.id][t][
                                'withdrawal_reason_type']
                        except KeyError:
                            pass

                        try:
                            validity_date = TEMP[dec.id][t]['validity_date']
                        except KeyError:
                            # Standard time used in reporting
                            # There is a special case to report outlooks on
                            # new ratings as informed in an email from ESMA
                            # on 2018-10-31, 14.43 with the validity datetime
                            # of the OT action later than the NW action
                            # (e.g. 1 minute later validity datetime).

                            validity_date = x.date_time_published

                except KeyError:

                    try:
                        owsd_status = TEMP[dec.id][t]['owsd_status']
                    except KeyError:
                        pass

                    try:
                        outlook_trend = TEMP[dec.id][t]['outlook_trend']
                    except KeyError:
                        pass

                    try:
                        watch_review = TEMP[dec.id][t]['watch_review']
                    except KeyError:
                        pass

                    try:
                        withdrawal_reason_type = TEMP[dec.id][t][
                            'withdrawal_reason_type']
                    except KeyError:
                        pass

                    try:
                        validity_date = TEMP[dec.id][t]['validity_date']
                    except KeyError:
                        # Standard time used in reporting
                        # There is a special case to report outlooks on
                        # new ratings as informed in an email from ESMA
                        # on 2018-10-31, 14.43 with the validity datetime
                        # of the OT action later than the NW action
                        # (e.g. 1 minute later validity datetime).

                        validity_date = x.date_time_published

                logger.info("           inserting records in db")

                # If this data point has already been inserted successfully,
                # skip to the next step
                if QTRatingCreateData.objects.filter(
                        hash=hash_key,
                        xml_file__status_code=1).exists():

                    # We have already reported this successfully
                    # work on next file instead
                    continue

                else:

                    create_rating_decision_xml_objects(
                        hash_key,
                        dec,
                        x,
                        validity_date,
                        t,
                        owsd_status,
                        outlook_trend,
                        watch_review,
                        withdrawal_reason_type,
                        rating_scale_id,
                        rating_value,
                        default_flag,
                        rated_object,
                        perspective,
                        issuer_rating_type_code,
                        debt_classification_code,
                        industry,
                        type_of_rating_for_erp,
                        relevant_for_cerep,
                        prev_rating_preliminary,
                        issues,
                        iss,
                        attributes,)
