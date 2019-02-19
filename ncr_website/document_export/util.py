"""Helper functions to generate pdf files.."""
import os
import tempfile
import unicodedata
import uuid
import pytz
import datetime

# Django
from django.http import HttpResponse
from django.template.loader import get_template

from PyPDF2 import PdfFileMerger

# Database
from datalake.gleif.command import GLEIFData
# Issue
from issue.models import Issue
from integrations.pdfreactor.utils.helper_function import html_file_2_pdf
# Issuer
from issuer.models import Issuer
from issuer.models.insider_log import InsiderLog
# Rating
from gui.templatetags.template_tags import (
    current_rating,
)
from rating.util.gui_toggles import gui_toggles
from rating_process.models.job_member import JobMember
from rating_process.models.methodology import RatingDecisionMethodologyLink
from rating.util.generate_rating_job_data import generate_rating_job_data

# Rating process
from rating_process.models.rating_decision import RatingDecision

# Util
from a_helper.other.sql import SQL
from upload.models import AnalyticalDocument
from integrations.s3.utils.helpers import download_file
from config.settings.base import AWS_ANALYTICAL_MEDIA_LOCATION

# https://niwinz.github.io/django-jinja/latest/
# create database connection and session
db_connection = SQL('datalake')


def generate_context(issuer_obj, rating_decision_obj, gleif_data, request):
    """Helper function to create a context variable to be sent to the
    templates."""

    if rating_decision_obj.date_time_committee:
        header_left_line_1 = 'Credit rating committee %s' % (
            rating_decision_obj.date_time_committee.strftime('%Y-%m-%d')
        )
    else:
        header_left_line_1 = 'Credit rating committee on [date not decided]'

    #####################################################
    # Existing rating decision score data
    #####################################################
    try:
        show_existing_scores = RatingDecision.objects.current_rating(
            issuer=issuer_obj).order_by('-id')[0]

    except:  # noqa E722
        show_existing_scores = False

    #####################################################
    # Existing rating decision score data
    #####################################################
    current_rating_obj = current_rating(issuer_obj)

    columns = {'show_rationale': False,
               'allow_edit': False}

    rating_commmittee_controller = gui_toggles(rating_decision_obj,
                                               show_existing_scores,
                                               **columns)

    # Create a link to the previous committee package
    if show_existing_scores:
        url = request.get_host()
        id_pair = str(issuer_obj.id) + '/' + str(show_existing_scores.id) + '/'

        previous_committee_package = ('<a href="http://' + url +
                                      '/issuer/committee_package/' + id_pair +
                                      '" target="_blank">Previous committee '
                                      'package</a> (needs improvement)')
    else:
        previous_committee_package = ''

    methodology_link_obj = RatingDecisionMethodologyLink.objects.filter(
        rating_decision=rating_decision_obj)

    try:
        previous_decision_comment = RatingDecision.objects.current_rating(
            issuer=issuer_obj)[0].committee_comments

        previous_decision_date = RatingDecision.objects.current_rating(
            issuer=issuer_obj)[0].date_time_committee

    except:  # noqa E722
        previous_decision_comment = False
        previous_decision_date = False

    if rating_decision_obj.has_passed_committee_date:
        rating_commmittee_controller['show_final_score'] = True
    else:
        rating_commmittee_controller['show_final_score'] = False

    gui_controls = {}
    auth = {'issuer': {
        'rating_job': {
            'edit': False,
            'view': True
        }
    }}
    datavalues = generate_rating_job_data(
        issuer_obj=issuer_obj,
        gui_controls=gui_controls,
        current_rating_obj=current_rating_obj,
        auth=auth,
        request=request,
        rating_decision_id=rating_decision_obj.id,)
    rating_decision_context = datavalues['context_data']

    rating_history = RatingDecision.objects.rating_history().filter(
        issuer=issuer_obj,
        date_time_published__lt=rating_decision_obj.date_time_committee)

    tz = pytz.timezone('Europe/Oslo')
    download_time = datetime.datetime.now(tz)

    context = {
        'environment': os.environ['ENVIRONMENT_MODE'],

        'data': {
            'gui': {
              'issuer': {
                  'issues': {
                      'show_existing': False,
                  }
              }
            },
            'issuer': {
                'data': issuer_obj,
                'current_rating': current_rating_obj,
                'issues':
                    Issue.objects.issue_list(
                        issuer_obj.id,
                        rating_decision_obj.date_time_committee),
                'rating_job': rating_decision_context,
                'rating_history': rating_history,
            }
        },
        'issuer': issuer_obj,

        'rating_decision': rating_decision_obj,

        'methodology': methodology_link_obj,

        'rating_controller': rating_commmittee_controller,

        'previous_committee_package': previous_committee_package,

        'previous_decision': previous_decision_comment,
        'previous_decision_date': previous_decision_date,

        ########
        # People
        ########
        'committee_members':
            JobMember.objects.confirmed_members().filter(
                rating_decision=rating_decision_obj,
                group_id=1),

        'header_left_line1': header_left_line_1,
        'header_left_line2': '',
        'header_right_line1':
            rating_decision_obj.event_type.description +
            ' (' + rating_decision_obj.rating_type.description.lower() + ')',

        'footer_left': 'Downloaded on: ' + download_time.strftime(
            "%Y-%m-%d, %H:%M"),
        'footer_mid': 'Security class 4: strictly confidential',

    }

    return context


def committee_pack(rating_decision_id, request):
    """Function to create the front pages for committee pack."""

    rating_decision_obj = RatingDecision.objects.get(pk=rating_decision_id)
    issuer_obj = Issuer.objects.get(pk=rating_decision_obj.issuer.id)

    template_file = 'issuer/rating_job/committee_package/main.html'

    gleif_data = GLEIFData(db_connection, issuer_obj.lei).return_data

    legal_name = gleif_data['entity'].legalname
    legal_name = str(unicodedata.normalize(
        'NFKD',
        legal_name).encode('ASCII',
                           'ignore').decode('utf-8'))

    target_file = (
        'Rating committee package for ' +
        legal_name +
        ' (' + datetime.datetime.today().strftime('%Y-%m-%d, %H%M') + ").pdf"
    )

    # Replace all Jinja2 variables with relevant data
    context = generate_context(
        issuer_obj, rating_decision_obj, gleif_data, request)

    # Return formatted as html
    rendered_html = get_template(template_file).render(context)

    f = tempfile.NamedTemporaryFile(mode='w+t',
                                    suffix='.html')
    f.write(rendered_html)

    cover_page_file = 'cover_pages_{}.pdf'.format(
        uuid.uuid4())
    html_file_2_pdf(f.name, cover_page_file)

    # Fetch uploaded files from AWS S3
    documents = AnalyticalDocument.objects.filter(
        issuer=issuer_obj,
        rating_decision=rating_decision_obj)

    # Merge pdf files into one
    pdfs = []
    pdfs.append(cover_page_file)

    # External analysis
    try:
        external_analysis_target = 'external_publ_' + issuer_obj.lei + '.pdf'

        filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
            documents.get(document_type__id=15).upload)
        download_file(filepath, external_analysis_target)
        pdfs.append(external_analysis_target)

    except AnalyticalDocument.DoesNotExist:

        try:
            external_analysis_target = 'external_' + issuer_obj.lei + '.pdf'
            filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
                documents.get(document_type__id=10).upload)
            download_file(filepath, external_analysis_target)
            pdfs.append(external_analysis_target)

        except AnalyticalDocument.DoesNotExist:

            pass

    # Internal analysis
    try:
        internal_analysis_target = 'internal_' + issuer_obj.lei + '.pdf'
        filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
            documents.get(document_type__id=11).upload)
        download_file(filepath, internal_analysis_target)
        pdfs.append(internal_analysis_target)
    except AnalyticalDocument.DoesNotExist:
        pass

    # Attachment #1
    try:
        attachment1_target = 'attachment_1_' + issuer_obj.lei + '.pdf'
        filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
            documents.get(document_type__id=12).upload)
        download_file(filepath, attachment1_target)
        pdfs.append(attachment1_target)

    except AnalyticalDocument.DoesNotExist:
        pass

    # Attachment #2
    try:
        attachment2_target = 'attachment_2_' + issuer_obj.lei + '.pdf'
        filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
            documents.get(document_type__id=13).upload)
        download_file(filepath, attachment2_target)
        pdfs.append(attachment2_target)

    except AnalyticalDocument.DoesNotExist:
        pass

    # Attachment #3
    try:
        attachment3_target = 'attachment_3_' + issuer_obj.lei + '.pdf'
        filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
            documents.get(document_type__id=14).upload)
        download_file(filepath, attachment3_target)
        pdfs.append(attachment3_target)

    except AnalyticalDocument.DoesNotExist:
        pass

    # Combine the files
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))

    # Temporary store on disk
    with open(target_file, 'wb') as fout:
        merger.write(fout)

    # Add page numbers
    add_page_number(target_file)

    response = HttpResponse(content=open(target_file, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename="%s"' % target_file

    # Delete all downloaded files
    for pdf in pdfs:
        os.unlink(pdf)

    os.unlink(target_file)

    return response


def external_report(request, id):
    """Genererate an external report."""

    template_file = 'issuer/reports/rating_report_cover.html'

    rating_decision_obj = RatingDecision.objects.get(pk=id)

    gleif_data = GLEIFData(db_connection,
                           rating_decision_obj.issuer.lei).return_data

    # Publish date
    publish_date = rating_decision_obj.date_time_published.strftime(
        '%-d %B %Y')

    # Sector
    issuer_type = rating_decision_obj.issuer.issuer_type.id
    if issuer_type == 1:
        sector = 'Corporate'
    elif issuer_type == 2:
        sector = 'Financial institutions'
    elif issuer_type == 3:
        sector = 'Real estate'

    # Type of rating
    rating_type = rating_decision_obj.event_type.id
    if rating_type == 1:
        rating_type = 'Rating initiation'
    elif rating_type == 2:
        rating_type = 'Rating action'
    elif rating_type == 3:
        rating_type = 'Annual review'

    # Replace all Jinja2 variables with relevant data
    context = {
        'data': {
            'issuer': {
                'gleif': gleif_data,
                'rating_job':
                    {
                        'data': rating_decision_obj,
                        'publish_date': publish_date,
                        'rating_decision': rating_decision_obj,
                        'sector': sector,
                        'rating_type': rating_type, }, }}}

    # Return formatted as html
    rendered_html = get_template(template_file).render(context)
    f = tempfile.NamedTemporaryFile(mode='w+t',
                                    suffix='.html')
    f.write(rendered_html)
    f.read()

    cover_page_file = 'cover_pages2.pdf'
    html_file_2_pdf(f.name, cover_page_file)

    response = HttpResponse(content=open(cover_page_file, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename="%s"' % cover_page_file

    os.unlink(cover_page_file)

    return response


def issuer_insider_list(request, id):
    """Genererate an external report."""

    template_file = 'issuer/compliance/insider_list.html'

    issuer_obj = Issuer.objects.get(pk=id)
    insiders = InsiderLog.objects.filter(issuer=issuer_obj).order_by(
        '-date_added',
        '-date_removed',
    )

    # Replace all Jinja2 variables with relevant data
    context = {
        'issuer': {
            'data': issuer_obj,
            'insider_log': insiders
        }}

    # Return formatted as html
    rendered_html = get_template(template_file).render(context)
    f = tempfile.NamedTemporaryFile(mode='w+t',
                                    suffix='.html')
    f.write(rendered_html)
    f.read()

    # Generate a unique file name
    cover_page_file = 'insider_list_{}.pdf'.format(
        uuid.uuid4())
    html_file_2_pdf(f.name, cover_page_file)

    response = HttpResponse(content=open(cover_page_file, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename="%s"' % cover_page_file

    os.unlink(cover_page_file)

    return response


def add_page_number(target_file):
    """Helper function to add page numbers to a pdf-file.

    Writes a pdf file containing page numbers.
    """

    from PyPDF2 import PdfFileReader
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from pdfrw import PdfReader, PdfWriter, PageMerge

    tmp_pagenum = 'wmark_' + target_file

    # Create object for page numbers
    c = canvas.Canvas(tmp_pagenum,
                      pagesize=A4, )

    # Read the target file
    input_pdf = PdfFileReader(open(target_file, 'rb'))

    # Count number of pages in the target file
    number_of_pages = input_pdf.getNumPages()

    # Loop through all pages in the target file and create a page number
    # in a new file. Not using
    for i in range(input_pdf.getNumPages()):
        text = '- Committee Pack, page ' + str((i + 1)) + ' / ' + str(
            number_of_pages) + ' -'

        c.setFont("Helvetica", 7)
        c.drawString(20,
                     8,
                     text,
                     )
        c.showPage()

    c.save()

    # Open the watermark file
    trailer = PdfReader(target_file)

    # Loop through the target file and append the page number
    for i, page in enumerate(trailer.pages):
        wmark = PageMerge().add(PdfReader(tmp_pagenum).pages[i])[0]

        PageMerge(page).add(wmark,
                            prepend=True).render()
    PdfWriter(target_file, trailer=trailer).write()

    # Cleanup
    os.unlink(tmp_pagenum)


def compress_pdf(pdf_file):
    """Use Ghostscript to compress pdf file."""

    import subprocess

    tmp_file = 'c_' + pdf_file

    command = [
        'ghostscript',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/printer',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        '-sOutputFile={}'.format(tmp_file),
        pdf_file
    ]

    subprocess.call(command)

    # Cleanup
    os.rename(tmp_file, pdf_file)
