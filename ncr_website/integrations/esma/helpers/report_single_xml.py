#!/usr/bin/python
"""This module allows sending a single XML-file to ESMA."""
import os
import sys
import getopt
import environ
import django

ROOT_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, ROOT_DIR)

# SETUP
# ------------------------------------------------------------------------------
# Load .env variables into OS Environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'
django.setup()

from integrations.esma.models.xml_file import XMLFile  # noqa: E402
from integrations.esma.utils.generic import parse_xml_data  # noqa: E402
from integrations.esma.const import (  # noqa: E402
    FILE_TYPE_RATING_QUANTITATIVE,
)


def main(argv):
    """Main function."""

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])

    except getopt.GetoptError:

        print('report_single_xml.py -hi <xml_file_id>')
        sys.exit(2)

    for opt, arg in opts:

        if opt == '-h':
            print('report_single_xml.py -i <xml_file_id>')
            sys.exit()

        elif opt in ("-i"):
            id = arg

    # Create XML and upload to ESMA
    try:
        xml_file = XMLFile.objects.get(pk=id)

        print('Parsing {}'.format(xml_file))

        parse_xml_data(xml_file, None, FILE_TYPE_RATING_QUANTITATIVE)

    except XMLFile.DoesNotExist as e:

        print("Error: {}".format(e))


if __name__ == "__main__":

    main(sys.argv[1:])
