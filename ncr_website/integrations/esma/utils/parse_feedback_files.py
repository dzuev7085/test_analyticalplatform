"""This module parses the XML-files that are returned by ESMA."""
import xmltodict
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def parse_feedback_file(xml_string):
    """Parse the data returned by ESMA after a file has been uploaded.
    :param str xml_string: an XML string containing the feedback data
    :returns: (int) 1 on success and 0 on failure
    """

    # Default to failure
    status_code = 0

    try:
        f = xmltodict.parse(xml_string)
    except Exception as e:
        logger.warning(e)

    try:
        if 'fdb:NoErrors' in f['fdb:FeedBackFileInfo']:
            # No errors reported, return success flag

            status_code = 1
    except KeyError:
        pass

    try:
        warning_error_type = f['fdb:FeedBackFileInfo'][
            'fdb:ErrorsInfo'][
            'fdb:ContentRatingRecords'][
            'fdb:ContentRatingErrorWarning'][
            'dtypes:WarningErrorType']

        if 'W' in warning_error_type:
            # This is a warning, not a fatal error, return success
            status_code = 1

        if 'E' in warning_error_type:
            # This is a fatal error, return failure
            status_code = 0

    except (KeyError, TypeError):
        pass

    return status_code
