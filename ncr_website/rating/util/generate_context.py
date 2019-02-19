"""This module generates context for a company."""
from datalake.gleif.command import GLEIFData, GLEIFEditor
from issue.forms import StamdataDataForm
from issue.models import Issue
from rating_process.models.rating_decision import RatingDecision
from gui.templatetags.template_tags import current_rating
from a_helper.other.sql import SQL
from upload.models import AnalyticalDocument
from rating.util.gui_toggles import gui_toggles
from issuer.models import Event, InsiderList, Issuer
from rating.util.generate_financial_statement import (
    generate_financial_statement
)
from rating.util.generate_rating_job_data import generate_rating_job_data
from upload.forms import AnalyticalDocumentForm


def return_company_context(request, pk, rating_decision_id=None,):
    """Generate context for the company view."""

    #####################################################
    # Initialize
    #####################################################
    db_connection = SQL('datalake')

    gui_controls = {}

    #####################################################
    # Get issuer information
    #####################################################
    issuer_obj = Issuer.objects.\
        select_related('issuer_type').\
        select_related('gics_sub_industry__industry__industry_group__sector').\
        select_related('address__country').\
        select_related('analyst__primary_analyst').\
        select_related('analyst__secondary_analyst').\
        select_related('relationship_manager').get(pk=pk)

    #####################################################
    # Authentication
    #####################################################
    group_list = request.user.groups.all().values('name')
    user_groups = []
    for group in group_list:
        user_groups.append(group['name'])

    auth = {'issuer': {
        'rating_job': {
            'edit': False,
            'view': False
        }
    }}
    if (request.user == issuer_obj.analyst.primary_analyst or
            request.user == issuer_obj.analyst.secondary_analyst):
        auth['issuer']['rating_job']['edit'] = True
    else:
        auth['issuer']['rating_job']['edit'] = False

    if 'Commercial' in user_groups:
        auth['issuer']['rating_job']['view'] = False
    else:
        auth['issuer']['rating_job']['view'] = True

    #####################################################
    # Current published rating
    #####################################################
    current_rating_obj = current_rating(issuer_obj)

    #####################################################
    # Get context data for rating decision
    #####################################################
    datavalues = generate_rating_job_data(
        issuer_obj=issuer_obj,
        gui_controls=gui_controls,
        current_rating_obj=current_rating_obj,
        auth=auth,
        request=request,
        rating_decision_id=rating_decision_id,)

    rating_decision_obj = datavalues['rating_decision_obj']
    rating_decision_context = datavalues['context_data']
    show_existing_scores = datavalues['show_existing_scores']
    error_messages = datavalues['error_messages']

    # We need to get the issuer type id as an int to ensure
    # consistency throughout the program.
    issuer_type_id = issuer_obj.issuer_type.description

    #####################################################
    # Create financial statement data
    #####################################################
    financial_statement = generate_financial_statement(issuer_obj)

    # Get data from GleiF database
    # If thinks break during issuer add, make sure we have a fall-back
    try:
        gleif_data = GLEIFData(db_connection, issuer_obj.lei).return_data
    except:  # noqa E722
        GLEIFEditor(db_connection).upsert(issuer_obj.lei)
        gleif_data = GLEIFData(db_connection, issuer_obj.lei).return_data

    #####################################################
    # Get all insiders
    #####################################################
    insider_list = []
    for insider in InsiderList.objects.filter(
        issuer=issuer_obj).order_by('contact_type',
                                    'first_name',
                                    'last_name'):
        insider_dict = insider.__dict__

        insider_dict.update(
            {'contact_type': insider.get_contact_type_display()})

        insider_dict.update({'allow_edit': True})

        insider_list.append(insider_dict)

    #####################################################
    # Events on issuer level
    #####################################################
    events = Event.objects.filter(
        issuer=issuer_obj).order_by(
        '-timestamp').select_related(
        'triggered_by_user').select_related('event_type')

    #####################################################
    # Rating decision and score data
    #####################################################

    # Modes
    # Either none or no hit on is_decided=False and date_time_published=Null:
    # => Show Create button
    # There is one where is_decided = 1 and date_time_published=null
    # => Show score page
    # There is one where is_decided = 0 and date_time_published=null
    # => Show score page

    gui_controls['rating_status'] = {}
    gui_controls['rating_status'].update({'enable': True})

    if not rating_decision_obj:
        gui_controls['rating'] = {'add_new_rating': True}

    analytical_document_upload_form = AnalyticalDocumentForm(
        instance=issuer_obj)

    #####################################################
    # List documents connected to issuer
    #####################################################
    analytical_documents = AnalyticalDocument.objects.filter(
        issuer=issuer_obj).order_by(
        'document_type', 'security_class').select_related(
        'security_class').select_related(
        'document_type').select_related('uploaded_by').select_related(
        'rating_decision')

    #####################################################
    # Auth
    #####################################################
    if 'Commercial' not in user_groups\
            and 'Compliance' not in user_groups:
        allow_edit = True
    else:
        allow_edit = False

    columns = {'show_rationale': True, 'allow_edit': allow_edit}

    rating_commmittee_controller = gui_toggles(rating_decision_obj,
                                               show_existing_scores,
                                               **columns)

    stamdataform = StamdataDataForm

    #####################################################
    # Context data sent to the template
    #####################################################
    context = {
        # Start working on the new format for passing data
        'gui': {
            'issuer': {
                'issues': {
                    'show_existing': True,
                }
            }
        },
        'data': {
            'issuer': {
                'data': issuer_obj,
                'current_rating': current_rating_obj,
                'financial_statement': financial_statement,
                'issues': Issue.objects.issue_list(issuer_obj.id,
                                                   '2999-12-31'),
                'rating_history':
                    RatingDecision.objects.rating_history().filter(
                        issuer=issuer_obj),
                'rating_job': rating_decision_context,
            }
        },

        'gui_controls': gui_controls,
        'rating_controller': rating_commmittee_controller,

        # TODO: Move up as this is depreceated
        'issuer': issuer_obj,

        'stamdataform': stamdataform,
        'auth': auth,

        'gleif': gleif_data,
        'error_messages': error_messages,
        'insider_list': insider_list,
        'issuer_type_id': issuer_type_id,
        'events': events,

        'analytical_documents': analytical_documents,
        'analytical_document_upload_form': analytical_document_upload_form,


    }

    return context
