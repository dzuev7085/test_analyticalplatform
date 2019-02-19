"""Helper function to convert a HTML file to pdf using PDF Reactor.
# https://www.pdfreactor.com/product/doc_html/index.html"""
from django.conf import settings as djangoSettings

from integrations.pdfreactor.utils.pdfreactor import PDFreactor


def html_file_2_pdf(input_file_path, output_file_name):
    """This function takes a HTML-formatted file and converts it
    to a pdf file using the PDF reactor framework."""

    if djangoSettings.ENVIRONMENT_MODE == 'DEV':
        pdf_reactor = PDFreactor("http://testap.nordiccreditrating.com:86/"
                                 "service/rest")

    else:
        pdf_reactor = PDFreactor("http://pdfreactor:9423/service/rest")

    config = {}
    if djangoSettings.ENVIRONMENT_MODE == 'DEV':
        config["enableDebugMode"] = True

    config["document"] = open(input_file_path).read()
    config["addLinks"] = True
    config["addBookmarks"] = True
    config["fullCompression"] = True
    config["documentDefaultLanguage"] = "en-GB"
    config["viewerPreferences"] = [
        PDFreactor.ViewerPreferences.FIT_WINDOW,
        PDFreactor.ViewerPreferences.PAGE_MODE_USE_THUMBS,
    ]
    config['javaScriptSettings'] = {
        'enabled': True,
    }

    result = pdf_reactor.convertAsBinary(config)

    # Check if successful
    if result is not None:
        file = open(output_file_name, 'wb')
        file.write(result)
        file.close()
