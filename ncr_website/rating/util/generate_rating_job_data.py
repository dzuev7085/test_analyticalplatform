"""Module to generate all context data needed for a rating job."""
import uuid
import subprocess
import datetime
from pycreditrating import (
    Rating as PCRRating,
    RATING_INDICATIVE_REVERSE
)
from issuer.models import OnboardingProcess
from methodology.models import Methodology
from rating_process.models.job_member import JobMember
from rating_process.models.internal_score_data import InternalScoreData
from rating_process.models.methodology import RatingDecisionMethodologyLink
from rating_process.models.questions import ControlQuestion
from rating_process.models.rating_decision_issue import RatingDecisionIssue
from rating_process.models.insider_link import RatingDecisionInsiderLink
from rating_process.models.process import Process
from rating_process.models.press_release import PressRelease
from rating_process.util import generate_rating_dict
from rating_process.models.rating_decision import RatingDecision
from datetime import timedelta
from django.conf import settings as djangoSettings
from rating_process.util import get_public_report, get_public_external_report
from integrations.s3.utils.helpers import download_file
from config.settings.base import AWS_ANALYTICAL_MEDIA_LOCATION
from a_helper.other.tasks import delete_files_task
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)


def generate_rating_job_data(issuer_obj,
                             gui_controls,
                             current_rating_obj,
                             auth,
                             request,
                             rating_decision_id=None):
    """
    Returns data for a specific rating job if rating_decision_id
    is specified, else takes last one

    :return: Dict content for rating_job
    """
    try:
        # Show an existing rating decision

        if rating_decision_id:
            rating_decision_obj = RatingDecision.objects. \
                select_related('rating_type').select_related('chair'). \
                get(pk=rating_decision_id)

        else:
            rating_decision_obj = RatingDecision.objects.filter(
                issuer=issuer_obj,
                date_time_deleted__isnull=True,
                date_time_published__isnull=True).select_related(
                'rating_type').select_related('chair')[0]

        # We need to be able to amend the error list with some custom errors
        error_messages = list(rating_decision_obj.error_messages)

        no_committee_members = JobMember.objects.confirmed_members().filter(
            rating_decision=rating_decision_obj
        ).count()
        if no_committee_members < 2:
            error_messages.append('Add more voting members, or make '
                                  'sure they confirm their attendance.')

        # Gui controls
        gui_controls['progress_bar'] = {}
        gui_controls['progress_bar'].update({'enable': True})
        gui_controls['progress_bar'].update({'ongoing_surveillance': False})

        # Store the current step in a shorter variable
        s = rating_decision_obj.get_process_step_display()

        if s == 'pre_committee':
            gui_controls['progress_bar'].update({'setup_done': True})

        elif s == 'analytical_phase':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done': True})

        elif s == 'post_committee':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done': True})
            gui_controls['progress_bar'].update({'analytical_phase_done':
                                                True})

        elif s == 'editor_phase':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done': True})
            gui_controls['progress_bar'].update({'analytical_phase_done':
                                                True})
            gui_controls['progress_bar'].update({'post_committee_done': True})

        elif s == 'issuer_confirmation_phase':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done':
                                                True})
            gui_controls['progress_bar'].update({'analytical_phase_done':
                                                True})
            gui_controls['progress_bar'].update({'post_committee_done': True})
            gui_controls['progress_bar'].update({'editing_done': True})

        elif s == 'analyst_final_approval_phase':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done': True})
            gui_controls['progress_bar'].update({'analytical_phase_done':
                                                True})
            gui_controls['progress_bar'].update({'post_committee_done': True})
            gui_controls['progress_bar'].update({'editing_done': True})
            gui_controls['progress_bar'].update({'issuer_confirmation_done':
                                                True})

        elif s == 'chair_final_approval_phase':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done': True})
            gui_controls['progress_bar'].update({'analytical_phase_done':
                                                True})
            gui_controls['progress_bar'].update({'post_committee_done': True})
            gui_controls['progress_bar'].update({'editing_done': True})
            gui_controls['progress_bar'].update({'issuer_confirmation_done':
                                                True})
            gui_controls['progress_bar'].update({'analyst_final_approval_done':
                                                True})

        elif s == 'publishing_phase' or s == 'publishing_phase_done':
            gui_controls['progress_bar'].update({'setup_done': True})
            gui_controls['progress_bar'].update({'pre_committee_done': True})
            gui_controls['progress_bar'].update({'analytical_phase_done':
                                                True})
            gui_controls['progress_bar'].update({'post_committee_done': True})
            gui_controls['progress_bar'].update({'editing_done': True})
            gui_controls['progress_bar'].update({'issuer_confirmation_done':
                                                True})
            gui_controls['progress_bar'].update({'analyst_final_approval_done':
                                                True})
            gui_controls['progress_bar'].update({'chair_final_approval_done':
                                                True})

        # Override settings on some of the steps
        if s == 'pre_committee' or s == 'chair_final_approval_phase':

            # Only chair may edit here
            if request.user == rating_decision_obj.chair:
                auth['issuer']['rating_job']['edit'] = True
            else:
                auth['issuer']['rating_job']['edit'] = False

        #####################################################
        # Subscores
        #####################################################
        subscores = {}

        internal_score_obj = InternalScoreData.objects.filter(
            rating_decision=rating_decision_obj
        ).all().order_by('subfactor__sort_order').select_related(
            'subfactor__factor')
        internal_score_obj_list = list(internal_score_obj)

        if issuer_obj.issuer_type.description == 1 or \
                issuer_obj.issuer_type.description == 3:

            subscores['business_risk'] = list(
                filter(lambda i: i.subfactor.factor.name == 'Business risk',
                       internal_score_obj_list))

            subscores['financial_risk_assessment'] = list(
                filter(lambda i: i.subfactor.factor.name == 'Financial risk',
                       internal_score_obj_list))

        elif issuer_obj.issuer_type.description == 2:

            subscores['operating_environment'] = list(
                filter(lambda i: i.subfactor.factor.name ==
                       'Operating environment',
                       internal_score_obj_list))

            subscores['risk_appetite'] = list(
                filter(lambda i: i.subfactor.factor.name == 'Risk appetite',
                       internal_score_obj_list))

            subscores['competitive_position'] = list(
                filter(lambda i: i.subfactor.factor.name ==
                       'Competitive position',
                       internal_score_obj_list))

            subscores['performance_indicators'] = list(
                filter(lambda i: i.subfactor.factor.name ==
                       'Performance indicators',
                       internal_score_obj_list))

        subscores['adjustment_factor'] = list(
            filter(lambda i: i.subfactor.factor.name == 'Adjustment factors',
                   internal_score_obj_list))

        subscores['support_factor'] = list(
            filter(lambda i: i.subfactor.factor.name == 'Support factors',
                   internal_score_obj_list))

        #####################################################
        # Existing issue subscore data
        #####################################################
        # Issue
        subscores['issue'] = RatingDecisionIssue.objects.filter(
            rating_decision=rating_decision_obj).all()

        #####################################################
        # Committee members
        #####################################################
        try:
            rating_committee_member_obj = JobMember.objects.filter(
                rating_decision=rating_decision_obj,
                group_id=1).select_related('member'). \
                select_related('role'). \
                select_related('group')
        except:  # noqa E722
            rating_committee_member_obj = False

        #####################################################
        # Editor
        #####################################################
        try:
            if rating_decision_obj:
                editor_obj = JobMember.objects.get(
                    rating_decision=rating_decision_obj,
                    group_id=2)
            else:
                editor_obj = False
        except:  # noqa E722
            editor_obj = False

        #####################################################
        # Insiders linked to rating job
        #####################################################
        try:
            rating_job_insiders_obj = \
                RatingDecisionInsiderLink.objects.filter(
                    rating_decision=rating_decision_obj).select_related(
                    'insider')
        except:  # noqa E722
            rating_job_insiders_obj = False

        #####################################################
        # Information about press release
        #####################################################
        try:
            if rating_decision_obj:
                press_release_obj = PressRelease.objects.get(
                    rating_decision=rating_decision_obj)

                if not press_release_obj.is_valid and \
                    rating_decision_obj.get_process_step_display() == \
                        'analyst_final_approval_phase':
                        error_messages.append('Fill in all fields of the '
                                              'press release.')
            else:
                press_release_obj = False

        except:  # noqa E722
            press_release_obj = False

        #####################################################
        # Questions
        #####################################################
        question_obj = ControlQuestion.objects.filter(
            rating_decision=rating_decision_obj).select_related(
            'question').select_related(
            'question__stage')

        control_questions = {
            'analyst_final_approval': question_obj.filter(
                question__stage=3),
            'chair_final_approval': question_obj.filter(
                question__stage=4),
            'publishing': question_obj.filter(
                question__stage=5)
        }

        #####################################################
        # Information about the process steps
        #####################################################
        try:
            if rating_decision_obj:
                process_obj = Process.objects.get(
                    rating_decision=rating_decision_obj)
            else:
                process_obj = False
        except:  # noqa E722
            process_obj = False

        #####################################################
        # Methodology
        #####################################################
        # Insert links between decision and methodology

        if rating_decision_obj:

            methodology_link_obj = RatingDecisionMethodologyLink.objects.\
                    filter(rating_decision=rating_decision_obj).select_related(
                        'methodology__category')

            if not methodology_link_obj:
                if issuer_obj.issuer_type.description == 1 or \
                        issuer_obj.issuer_type.description == 3:
                    # Corporate
                    # Always pick latest
                    methodology_id = 1

                else:
                    # Financial
                    methodology_id = 2

                try:
                    methodology_obj = Methodology.objects.order_by(
                        'category__name', '-date_decision').filter(
                        date_deleted__isnull=True,
                        category__id=methodology_id).distinct(
                        'category__name')[0]

                    RatingDecisionMethodologyLink.objects.create(
                        rating_decision=rating_decision_obj,
                        methodology=methodology_obj
                    )

                    # Rating principles
                    methodology_rating_criteria_obj = Methodology.objects.\
                        order_by('category__name', '-date_decision').filter(
                            date_deleted__isnull=True,
                            category__id=3).distinct('category__name')[0]

                    RatingDecisionMethodologyLink.objects.create(
                        rating_decision=rating_decision_obj,
                        methodology=methodology_rating_criteria_obj
                    )

                    methodology_link_obj = RatingDecisionMethodologyLink. \
                        objects.filter(rating_decision=rating_decision_obj)
                except:  # noqa E722
                    methodology_link_obj = []

        else:
            methodology_link_obj = []

        #####################################################
        # Calculated ratings
        #####################################################

        # Decided rating
        try:
            decided_calculated_rating = PCRRating(
                generate_rating_dict(
                    issuer_obj.issuer_type.description,
                    internal_score_obj_list,
                    'decided'))
        except:  # noqa E722
            decided_calculated_rating = False

        # Proposed rating
        try:
            proposed_calculated_rating = PCRRating(
                generate_rating_dict(issuer_obj.issuer_type.description,
                                     internal_score_obj_list,
                                     'proposed'))
        except:  # noqa E722
            proposed_calculated_rating = False

        if rating_decision_obj.process_step >= 3:

            if not proposed_calculated_rating.weight_check \
                    or not decided_calculated_rating.weight_check:
                error_messages.append(
                    'The impact weights do not sum to 100%, but {:.1%}.'.
                    format(proposed_calculated_rating.weight))

            else:
                if proposed_calculated_rating.issuer_rating is None \
                        or decided_calculated_rating.issuer_rating is None:
                    error_messages.append('Not all sub scores are set.')
            onboarding_obj = OnboardingProcess.objects.get(issuer=issuer_obj)

            if onboarding_obj.instrument_rating:

                if len(subscores['issue']) == 0:

                    error_messages.append('The issues has requested issue '
                                          'ratings, add ratings for seniority '
                                          'levels.')

                if len(subscores['issue']) > 0 and \
                        rating_decision_obj.process_step >= 4:

                    _e_list = []
                    for issue in subscores['issue']:
                        if issue.decided_lt is None:
                            _e_list.append(1)

                    if sum(_e_list) > 0:
                        error_messages.append('Assign ratings for seniority '
                                              'levels.')

        #####################################################
        # Existing rating decision score data
        #####################################################
        try:
            show_existing_scores = rating_decision_obj.previous_rating

            existing_scores = {}
            if show_existing_scores:

                internal_score_existing_obj = InternalScoreData.objects.filter(
                    rating_decision=show_existing_scores)

                if internal_score_existing_obj:

                    internal_score_existing_obj_values = \
                        internal_score_existing_obj.\
                        values('subfactor_id',
                               'decided_notch_adjustment',
                               'decided_score')

                    for i in internal_score_existing_obj_values:
                        decided_score = i['decided_score']
                        decided_notch = i['decided_notch_adjustment']

                        try:
                            decided_score = RATING_INDICATIVE_REVERSE[
                                                decided_score].lower() + \
                                            ' (' + str(decided_score) + ')'
                        except KeyError:
                            decided_score = None

                        existing_scores[i['subfactor_id']] = {
                            'decided_notch_adjustment': decided_notch,
                            'decided_score': decided_score
                        }

            # Return existing rating
            try:

                if internal_score_existing_obj:
                    existing_calculated_rating = PCRRating(
                        generate_rating_dict(
                            issuer_obj.issuer_type.description,
                            list(internal_score_existing_obj),
                            'decided'))
                else:
                    existing_calculated_rating = 'n/a'
            except:  # noqa E722
                existing_calculated_rating = 'n/a'


        except:  # noqa E722
            existing_calculated_rating = 'n/a'
            existing_scores = False

        #####################################################
        # Previews of images
        #####################################################

        tmp_file_name_thumb = None
        tmp_external_file_name_thumb = None

        try:
            if s == 'editor_phase' or s == 'chair_final_approval_phase' or \
                    s == 'publishing_phase':

                # Define file paths
                tmp_file_name = 'dl_{}.pdf'.format(uuid.uuid4())
                fp = djangoSettings.BASE_DIR + '/tmp/'
                target_file = fp + tmp_file_name

                # Get ID# of report
                if s == 'chair_final_approval_phase' or \
                        s == 'publishing_phase':

                    tmp_external_file_name_thumb = tmp_file_name + '_thumb.jpg'

                    # Display the report that will be published externally
                    document = get_public_external_report(rating_decision_obj)

                    target_file_tmp = fp + tmp_external_file_name_thumb

                else:
                    tmp_file_name_thumb = tmp_file_name + '_thumb.jpg'

                    # Setup file names
                    target_file_tmp = fp + tmp_file_name_thumb

                    document = get_public_report(rating_decision_obj)

                # Point to file location at AWS
                filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
                    document.upload)

                # Download file from AWS S3
                download_file(filepath, target_file)

                # Use MagicImage to convert pdf to img
                params = ['convert', target_file + '[0]', target_file_tmp]
                subprocess.check_call(params)

                # Delete the files in the future to avoid race condition
                later = datetime.datetime.utcnow() + timedelta(minutes=3)
                delete_files_task.apply_async(
                    [target_file_tmp,
                     target_file],
                    eta=later
                )
        except Exception as e:
            logger.error(e)

    except:  # noqa E722

        existing_calculated_rating = 'n/a'
        existing_scores = False
        tmp_file_name_thumb = None
        tmp_external_file_name_thumb = None
        proposed_calculated_rating = False
        decided_calculated_rating = False
        methodology_link_obj = []
        process_obj = False
        press_release_obj = False
        rating_job_insiders_obj = False
        rating_decision_obj = False
        editor_obj = False
        subscores = False
        control_questions = False
        show_existing_scores = False
        rating_committee_member_obj = False
        error_messages = []

    context_data = {'proposed_rating': proposed_calculated_rating,
                    'decided_rating': decided_calculated_rating,
                    'rating_job_insiders': rating_job_insiders_obj,
                    'process': process_obj,
                    'committee_members': rating_committee_member_obj,
                    'editors': editor_obj,
                    'methodologies': methodology_link_obj,
                    'subscores': subscores,
                    'rating_decision': rating_decision_obj,
                    'press_release': press_release_obj,
                    'control_questions': control_questions,
                    'preview': {
                        'internal_external_pdf': tmp_file_name_thumb,
                        'external_pdf':          tmp_external_file_name_thumb,
                    },
                    'existing': {
                        'scores': existing_scores,
                        'calc_rating': existing_calculated_rating,
                        'decision': current_rating_obj, }, }

    return_dict = {
        'rating_decision_obj': rating_decision_obj,
        'show_existing_scores': show_existing_scores,
        'context_data': context_data,
        'error_messages': error_messages,
    }

    return return_dict
