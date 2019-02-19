"""Tasks to send data to ESMA."""
from celery import shared_task
from celery.utils.log import get_task_logger

from integrations.esma.models.xml_file import XMLFile
from integrations.esma.utils.populate_cra_info import populate_cra_info
from integrations.esma.utils.populate_lead_analyst import populate_lead_analyst
from integrations.esma.utils.populate_debt_classification import (
    populate_debt_classification
)
from integrations.esma.utils.populate_issuer_rating import (
    populate_issuer_rating
)
from integrations.esma.utils.populate_issue_program import (
    populate_issue_program
)
from integrations.esma.utils.populate_rating_scale import (
    populate_rating_scale
)
from integrations.esma.const import (
    FILE_TYPE_RATING_QUALITATIVE,
    FILE_TYPE_LOOKUP,
    FILE_TYPE_RATING_QUANTITATIVE,

)
from integrations.esma.utils.populate_rating_decision import (
    populate_rating_decision
)
from integrations.esma.utils.generic import parse_xml_data


logger = get_task_logger(__name__)


@shared_task()
def update_qualitative_rating_info():
    """Send qualitative rating data to ESMA."""

    """CRA info."""
    logger.info("Updating CRA info...")

    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
    )
    populate_cra_info(xml_file)
    parse_xml_data(xml_file, 'cra_info', data_type='DATQXX')

    """Lead analyst."""
    logger.info("Updating lead analyst info...")
    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
    )
    populate_lead_analyst(xml_file)
    parse_xml_data(xml_file, 'lead_analyst_list')

    """Debt classification."""
    logger.info("Updating debt classification info ...")
    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
    )
    populate_debt_classification(xml_file)
    parse_xml_data(xml_file, 'issuer_rated_debt_classification_list')

    """Issuer rating."""
    logger.info("Updating issuer rating info ...")
    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
    )
    populate_issuer_rating(xml_file)
    parse_xml_data(xml_file, 'issuer_rating_list')

    """Issue program."""
    logger.info("Updating issue program info ...")
    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
    )
    populate_issue_program(xml_file)
    parse_xml_data(xml_file, 'issue_program_list')

    """Rating scale."""
    logger.info("Updating rating scale info ...")
    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
    )
    populate_rating_scale(xml_file)
    parse_xml_data(xml_file, 'rating_scale_list')


@shared_task()
def update_quantatative_rating_info():
    """Send quantative rating data to ESMA."""

    # Set all stale objects to unsuccessful
    XMLFile.objects.filter(file_type=2,
                           status_code__isnull=True).update(status_code=0)

    # Loop through recent rating decisions
    populate_rating_decision(issues=False)

    # Loop through recent issue rating decisions
    populate_rating_decision(issues=True)

    # Take the row that was created first
    for xml_file in XMLFile.objects.filter(
            file_type=2, status_code__isnull=True).order_by('id'):

        # Create XML and upload to ESMA
        parse_xml_data(xml_file, None, FILE_TYPE_RATING_QUANTITATIVE)


@shared_task()
def update_esma_qualitative():
    """Send qualitative data to ESMA."""

    logger.info("ESMA: check for qualitative rating updates to send.")
    update_qualitative_rating_info()
    logger.info("ESMA: finish check for qualitative rating updates.")


@shared_task()
def update_esma_quantitative():
    """Send quantative data to ESMA."""

    logger.info("ESMA: check for quantative rating updates to send.")
    update_quantatative_rating_info()
    logger.info("ESMA: finish check for quantitative rating updates.")
