"""Generic utils for ESMA reporting."""
import tempfile
import datetime
from datetime import timedelta
import os
import errno
import shutil
import sys
from lxml import etree
from django.template.loader import get_template
from xhtml2pdf import pisa
from integrations.utils.sftp import sftp_upload_file, sftp_download_file
from django.core.files import File
from integrations.esma.utils.parse_feedback_files import (
    parse_feedback_file
)
from pyesmaradar import (
    NSMAP_RATING_QUALITATIVE,
    NS_RATING_QUALITATIVE,
    NS_RATING_QUALITATIVE_SCHEMA_LOCATION,
    NS_RATING_QUALITATIVE_VERSION,
    QualitativeData,

    NSMAP_RATING_QUANTATIVE,
    NS_RATING_QUANTITATIVE,
    NS_RATING_QUANTITATIVE_SCHEMA_LOCATION,
    NS_RATING_QUANTITATIVE_VERSION,
    QuantitativeData,

    Validator,
)

from django.conf import settings

from upload.models import AnalyticalDocument
from integrations.s3.utils.helpers import download_file
from celery.utils.log import get_task_logger

from a_helper.other.tasks import delete_files_task

from a_helper.mail.tasks import send_email
from integrations.esma.utils.hash_functions import create_hash
from integrations.esma.models.reporting_type_info import ReportingTypeInfo
from integrations.esma.const import ATTR_UPDATED_STR
from integrations.esma.utils.create_dicts import (
    return_lead_analyst_list,
    return_debt_classification_list,
    return_issue_program_list,
    return_issuer_rating_list,
    return_rating_scale_list,
    return_cra_info,
    return_rating_quantitative
)

from integrations.esma.const import (
    NCR_LEI,
    ROOT_RATING_DATA_REPORT,
    FILE_TYPE_RATING_QUALITATIVE,
    NCR_HUB_RECIPIENT,
    FILE_TYPE_RATING_QUANTITATIVE,
)

logger = get_task_logger(__name__)


STATUS_MAP = {
    1: 'Success',
    0: 'Failure',
}


def get_or_create_reporting_type_info(reporting_type,
                                      change_reason,
                                      reporting_reason_text,
                                      hash_string):
    """Use a hash string to create a unique ReportingTypeInfo record."""

    hash = create_hash(hash_string)

    # Create a new ReportingTypeInfo record
    reporting_type_info, _ = ReportingTypeInfo.objects.get_or_create(
        reporting_type=reporting_type,
        change_reason=change_reason,
        reporting_reason=reporting_reason_text,
        hash=hash
    )

    return (reporting_type_info, _)


def create_reporting_reason_string(reporting_reason):
    """Return a reporting reason joined from a list of reasons."""

    reporting_reason_exp = ", ".join(reporting_reason)
    return ATTR_UPDATED_STR + ': ' + reporting_reason_exp


def create_setup_dict(type, xml_file):
    """Return the setup dict."""

    SETUP = {}

    if type == 'rating_qualitative':

        SETUP = {'file_sequence_number': xml_file.sequence_number,
                 'file_type': FILE_TYPE_RATING_QUALITATIVE,
                 'hub_recipient': NCR_HUB_RECIPIENT,
                 'reporting_lei': NCR_LEI,
                 'esma_cra_code': settings.ESMA_CRA_CODE,
                 'root': ROOT_RATING_DATA_REPORT,
                 'version': NS_RATING_QUALITATIVE_VERSION,
                 'nsmap': {'nsmap': NSMAP_RATING_QUALITATIVE,
                           'root': NS_RATING_QUALITATIVE,
                           'schema_location':
                               NS_RATING_QUALITATIVE_SCHEMA_LOCATION}}

    elif type == 'rating_quantitative':

        SETUP = {'file_sequence_number': xml_file.sequence_number,
                 'file_type': FILE_TYPE_RATING_QUANTITATIVE,
                 'hub_recipient': NCR_HUB_RECIPIENT,
                 'reporting_lei': NCR_LEI,
                 'esma_cra_code': settings.ESMA_CRA_CODE,
                 'root': ROOT_RATING_DATA_REPORT,
                 'version': NS_RATING_QUANTITATIVE_VERSION,
                 'nsmap': {'nsmap': NSMAP_RATING_QUANTATIVE,
                           'root': NS_RATING_QUANTITATIVE,
                           'schema_location':
                               NS_RATING_QUANTITATIVE_SCHEMA_LOCATION}
                 }

    return SETUP


def create_rating_qualitative_dict(type, xml_file):
    """Create a dict with qualitative rating data"""

    SETUP = create_setup_dict('rating_qualitative', xml_file)

    BASE = {
        'setup': SETUP,
    }

    if type == 'cra_info':
        data = return_cra_info(xml_file)

        if data:
            BASE['qualitative_data_report_info'] = {
                'cra_info': data,
            }
        else:
            BASE = False

    elif type == 'issuer_rating_list':
        data = return_issuer_rating_list(xml_file)

        if data:
            BASE['qualitative_data_report_info'] = {
                'issuer_rating_list': data,
            }
        else:
            BASE = False

    elif type == 'issuer_rated_debt_classification_list':
        data = return_debt_classification_list(xml_file)

        if data:
            BASE['qualitative_data_report_info'] = {
                'issuer_rated_debt_classification_list': data,
            }
        else:
            BASE = False

    elif type == 'issue_program_list':
        data = return_issue_program_list(xml_file)

        if data:
            BASE['qualitative_data_report_info'] = {
                'issue_program_list':
                    return_issue_program_list(xml_file),
            }
        else:
            BASE = False

    elif type == 'lead_analyst_list':
        data = return_lead_analyst_list(xml_file)

        if data:
            BASE['qualitative_data_report_info'] = {
                'lead_analyst_list': data,
            }
        else:
            BASE = False

    elif type == 'rating_scale_list':
        data = return_rating_scale_list(xml_file)

        if data:
            BASE['qualitative_data_report_info'] = {
                'rating_scale_list': data,
            }
        else:
            BASE = False

    return BASE


def create_send_file(xml_object, xml_file, data_type=None, data=None):
    """Create and send a file to ESMA based on
    XML input"""

    xmlstring = etree.tostring(xml_object.xml,
                               pretty_print=True,
                               xml_declaration=True,
                               encoding='UTF-8')

    """Next step: create folder and save file on disk."""
    try:
        os.mkdir(xml_object.file_name)
    except OSError as e:
        """An error occured: elete XML-file record"""

        xml_file.status_code = 0
        xml_file.save()

        if e.errno != errno.EEXIST:
            raise
    file_path = os.path.join(xml_object.file_name,
                             xml_object.file_name + ".xml")
    file_handle = open(file_path, "wb")
    file_handle.write(xmlstring)
    file_handle.close()

    xsd_path = str(os.path.join(settings.BASE_DIR + "/integrations/esma/xsd"))

    """Next step: validate XML against schema."""
    if data_type == 'DATRXX':
        xml_schema = os.path.join(
            xsd_path,
            "rating",
            "CRA3_" + FILE_TYPE_RATING_QUANTITATIVE +
            NS_RATING_QUANTITATIVE_VERSION + ".xsd")
    else:
        xml_schema = os.path.join(
            xsd_path,
            "rating",
            "CRA3_" + FILE_TYPE_RATING_QUALITATIVE +
            NS_RATING_QUALITATIVE_VERSION + ".xsd")

    validator = Validator(xml_schema)

    try:
        validator.validate(open(file_path))

    except Exception as e:
        xml_file.status_code = 0
        xml_file.save()

        """Step out of program on validation error."""
        logger.info("Validation error: " + str(e))
        print(str(e))
        sys.exit()

    # We should try to create the reports
    # TODO: fix here for issues
    if data_type == 'DATRXX':
        """If successful validation, download external report and name
        correctly."""
        create_research_report(data, xml_file, xml_object)

        """If successful validation, create press release and name
        correctly."""
        create_press_release(data, xml_file, xml_object)

    """Next step: put folder contents in zip file"""
    shutil.make_archive(xml_object.file_name, 'zip', xml_object.file_name)

    zip_file_name = xml_object.file_name + ".zip"
    abs_file_path = os.path.abspath(zip_file_name)

    """Next step: upload to ESMA."""
    sftp_upload_file(host=settings.ESMA_HOST,
                     port=6710,
                     user=settings.ESMA_USER_RATING,
                     password=settings.ESMA_PASSWORD_RATING,
                     local_path=abs_file_path,
                     remote_path='/outgoing/' + zip_file_name,)

    # We have successfully uploaded the file, so there is a legal
    # requirement to save the file for five years
    f = open(zip_file_name, 'rb')
    myfile = File(f)

    xml_file.document_location.save(
        name=zip_file_name,
        content=myfile)

    return zip_file_name


def parse_xml_data(xml_file, file_type, data_type=None):
    """Parse a dict into XML and upload file."""

    logger.info(xml_file)

    DATA = {}

    # Returns false if unsucessful in creating dict
    try:
        if data_type == 'DATRXX':
            DATA['setup'] = create_setup_dict('rating_quantitative', xml_file)
            DATA.update(return_rating_quantitative(xml_file))

        else:
            DATA = create_rating_qualitative_dict(type=file_type,
                                                  xml_file=xml_file)
    except Exception as e:
        logger.info("Error creating dict: " + str(e))

    if DATA:
        logger.info("Created data dict.")

        try:
            if data_type == 'DATRXX':
                xml_object = QuantitativeData(DATA)
            else:
                xml_object = QualitativeData(DATA)
        except Exception as e:
            logger.info("Error creating xml object: " + str(e))

        logger.info("Created XML-object")

        # Create the XML-file and upload it
        # function returns name of created file
        zip_file_name = create_send_file(xml_object, xml_file, data_type, DATA)
        logger.info("Created zip file")

        # The idea here is to look for the file in the incoming folder
        # The file only sits in the folder for a very short time and is then
        # moved to the archive/incomning folder.
        # Thus, look in the forst folder, time out and then look in the second
        # folder
        try:
            dl_file = sftp_download_file(
                host=settings.ESMA_HOST,
                user=settings.ESMA_USER_RATING,
                port=6710,
                password=settings.ESMA_PASSWORD_RATING,
                remote_path='incoming/',
                look_for=zip_file_name[19:28],
                timeout=60*4)

        except FileNotFoundError:

            try:
                dl_file = sftp_download_file(
                    host=settings.ESMA_HOST,
                    user=settings.ESMA_USER_RATING,
                    port=6710,
                    password=settings.ESMA_PASSWORD_RATING,
                    remote_path='archive/incoming/',
                    look_for=zip_file_name[19:28],
                    timeout=60 * 4)

            except FileNotFoundError as e:

                logger.critical(e)

        shutil.unpack_archive(filename=dl_file, format='zip')

        logger.info("Downloaded file from ESMA")

        # Save file to AWS
        f = open(dl_file, 'rb')
        myfile = File(f)

        xml_file.response_file.save(
            name=dl_file,
            content=myfile)

        """Read contents of XML-file"""
        xml_file_path = os.path.abspath(dl_file[0:28] + '.xml')
        e = etree.parse(xml_file_path)
        feedback = etree.tostring(e)

        status_code = parse_feedback_file(feedback)

        logger.info("Read file from ESMA")

        header = (
            os.environ['ENVIRONMENT_MODE'] +
            ' | ESMA reporting and feedback | {}'.format(
                STATUS_MAP[status_code]))

        sent_file = os.path.abspath(xml_object.file_name +
                                    '/' +
                                    xml_object.file_name + '.xml')
        received_file = os.path.abspath(dl_file[0:28] + '.xml')

        attachments = [
            sent_file,
            received_file
        ]

        send_list = ['patrik.lindgren@nordiccreditrating.com']

        # We want to notify Compliance in production
        if os.environ['ENVIRONMENT_MODE'] == 'PROD':
            send_list.append('compliance@nordiccreditrating.com')

        logger.info("Created send list")

        body = """File sequence: {}
Status: {}

Return message:
{}""".format(
            xml_file.sequence_number,
            STATUS_MAP[status_code],
            feedback
        )

        send_email.delay(header=header,
                         body=body,
                         to=send_list,
                         attachments=attachments)

        logger.info("Sent email")

        # Save the status of the uploaded file
        xml_file.status_code = status_code
        xml_file.save()

        # Cleanup of files
        # Delay 10 minutes so that the mail has been sent
        # If we dont delay, there is a risk of a race condition
        # where the files have been deleted before the files
        # have been sent
        logger.info("Adding file number {} to delete que".format(
            xml_file.sequence_number
        ))
        later = datetime.datetime.utcnow() + timedelta(minutes=10)
        files = [
                    os.path.abspath(zip_file_name),
                    os.path.abspath(dl_file),
                    os.path.abspath(xml_file_path),
                    os.path.abspath(xml_object.file_name)
                ]
        delete_files_task.apply_async(files, eta=later)

        logger.info("   Updated {} | sequence: {}".format(
            file_type,
            xml_file.sequence_number))

    else:
        logger.info("   {}: no data to update".format(file_type))

        # Delete the file record created above
        xml_file.delete()


def create_research_report(data, xml_file, xml_object):
    """
    Download and put in correct place a research report.

    :param data: dict containing information about decision
    :param xml_file: XMLFile object
    :param xml_object: XML object created from data and xml_file
    """

    try:
        research_report = AnalyticalDocument.objects.get(
            pk=xml_file.qtratingcreatedata.qtratingactioninfo.
            research_report.pk)

        f = os.path.join(xml_object.file_name,
                         data['rating_create_data']['rating_action_info'][
                             'research_report']['research_report_file_name']
                         + '.pdf')

        research_report_file_path = settings.AWS_ANALYTICAL_MEDIA_LOCATION +\
            '/' + str(research_report.upload)

        download_file(research_report_file_path, f)

    except AttributeError:
        # Catch the error where there is no press release, eg for issues
        # where the decision was made inbetween of committees

        pass


def create_press_release(data, xml_file, xml_object):
    """
    Create a press release in pdf format and put in correct place.

    :param data: dict containing information about decision
    :param xml_file: XMLFile object
    :param xml_object: XML object created from data and xml_file
    """

    try:
        press_release_obj = xml_file.qtratingcreatedata.qtratingactioninfo.\
            press_release

        template_file = 'issuer/reports/press_release.html'

        file_name = os.path.join(
            xml_object.file_name,
            data['rating_create_data']['rating_action_info'][
                'press_release']['press_release_file_name'] + '.pdf')

        context = {
            'validity_date':
                xml_file.qtratingcreatedata.
                qtratingactioninfo.qtactiondateinfo.validity_date.
                strftime('%Y-%m-%d'),
            'header': press_release_obj.header,
            'pre_amble': press_release_obj.pre_amble,
            'body': press_release_obj.body,
        }

        rendered_html = get_template(template_file).render(context)
        f = tempfile.NamedTemporaryFile(mode='w+t',
                                        suffix='.html')
        f.write(rendered_html)
        f.read()
        html = open(f.name).read()

        resultFile = open(file_name, "w+b")

        # convert HTML to PDF
        pisa.CreatePDF(
            html,
            dest=resultFile,
        )

        # close output file
        resultFile.close()

    except AttributeError:
        # Catch the error where there is no press release, eg for issues
        # where the decision was made inbetween of committees

        pass
