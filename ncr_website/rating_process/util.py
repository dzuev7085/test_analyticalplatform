"""Util functions for rating process."""
import unicodedata
import datetime
from datetime import timedelta
import os
from os import urandom

from integrations.s3.utils.helpers import download_file
from config.settings.base import AWS_ANALYTICAL_MEDIA_LOCATION
from upload.models import AnalyticalDocument

from .models.insider_link import RatingDecisionInsiderLink
from .const import (
    ISSUER_EMAIL,
    ISSUER_HEADER,
    ISSUER_EMAIL_HEADER_PASSWORD,
    ISSUER_EMAIL_BODY_PASSWORD
)

import PyPDF2

from a_helper.mail.tasks import send_email
from a_helper.other.tasks import delete_files_task


def get_public_report(rating_decision_obj):
    """Get document reference for external analysis. This is the document
    used internally and sent to the issuer.

    :param RatingDecision: rating decision object
    :returns: AnalyticalDocument object
    """

    return AnalyticalDocument.objects.get(
        issuer=rating_decision_obj.issuer,
        rating_decision=rating_decision_obj,
        document_type__id=10)


def get_public_external_report(rating_decision_obj):
    """Get document reference for external analysis. This is the document
    that will be published externally.

    :param RatingDecision: rating decision object
    :returns: AnalyticalDocument object
    """

    return AnalyticalDocument.objects.get(
        issuer=rating_decision_obj.issuer,
        rating_decision=rating_decision_obj,
        document_type__id=15)


def send_public_report(rating_decision_obj):
    """
    Download public report from AWS S3 and send to issuer.

    :param RatingDecision: rating decision object
    """
    target_file = None

    # Send this file to the issuer
    # Fetch uploaded files from AWS S3
    document = get_public_report(rating_decision_obj)

    try:
        legal_name = rating_decision_obj.issuer.legal_name
        legal_name = str(unicodedata.normalize(
            'NFKD',
            legal_name).encode('ASCII',
                               'ignore').decode('utf-8'))

        target_file = (
            legal_name +
            ' draft report' +
            ' (' + datetime.datetime.today().strftime(
                '%Y-%m-%d, %H%M') + ").pdf"
        )

        filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(
            document.upload)

        download_file(filepath, target_file)

        # Password protect file
        path, filename = os.path.split(target_file)
        output_file = os.path.join(path, "temp_" + filename)
        output = PyPDF2.PdfFileWriter()
        input_stream = PyPDF2.PdfFileReader(open(target_file, "rb"))

        for i in range(0, input_stream.getNumPages()):
            output.addPage(input_stream.getPage(i))

        outputStream = open(output_file, "wb")

        user_password = urandom(16).hex()[:5]

        # Set user and owner password to pdf file
        output.encrypt(user_pwd=user_password,
                       owner_pwd='owner_pass',
                       use_128bit=True)
        output.write(outputStream)
        outputStream.close()

        # Rename temporary output file with original filename, this
        # will automatically delete temporary file
        os.rename(output_file, target_file)

        attachments = []  # start with an empty list

        # add the attachment to the list
        attachments.append(target_file)

        contact_list = list(RatingDecisionInsiderLink.objects.filter(
            rating_decision=rating_decision_obj
        ))

        to_list = []
        for row in contact_list:
            to_list.append(row.insider.email)

        # Send email with link to admin control to editor
        send_email.delay(
            header=ISSUER_HEADER,
            body=ISSUER_EMAIL % (
                rating_decision_obj.issuer.analyst.primary_analyst.
                first_name),
            to=to_list,
            from_sender=None,
            cc=rating_decision_obj.issuer.analyst.primary_analyst.
            email,
            attachments=attachments)

        # Send email with password to primary analyst
        send_email.delay(
            header=ISSUER_EMAIL_HEADER_PASSWORD,
            body=ISSUER_EMAIL_BODY_PASSWORD.format(
                target_file,
                user_password,
                rating_decision_obj.issuer.analyst.primary_analyst.
                first_name
            ),
            to=to_list,
            from_sender=None,
            cc=rating_decision_obj.issuer.analyst.primary_analyst.
            email,
        )

        # Delete file
        later = datetime.datetime.utcnow() + timedelta(minutes=10)
        files = [os.path.abspath(target_file)]
        delete_files_task.apply_async(files, eta=later)

    except AnalyticalDocument.DoesNotExist:
        pass


def value_lambda(internal_score_obj, subfactor, factor):
    """Filter rating decision object without hitting the db."""

    return getattr(list(filter(lambda i: i.subfactor.id == subfactor,
                               internal_score_obj))[0], factor)


def generate_rating_dict(issuer_type_id, internal_score_obj, type, version=1):
    """Create a json string representing a rating.

    :param issuer_type_id: integer representing the type of issuer
    :param internal_score_obj: django queryset
    :param type: decided or proposed
    :return: json with dating data
    """

    try:
        BOOL_MAP = {
            True: 1,
            False: 0,
        }

        hl = internal_score_obj[0].assessment.highestlowest

        highest_lowest = {
            'is_AAA': BOOL_MAP[hl.is_aaa],
            'is_AA_plus': BOOL_MAP[hl.is_aa_plus],
            'is_CCC': BOOL_MAP[hl.is_ccc],
            'is_CC': BOOL_MAP[hl.is_cc],
            'is_C': BOOL_MAP[hl.is_c],
        }

    except Exception:

        highest_lowest = {
            'is_AAA': 0,
            'is_AA_plus': 0,
            'is_CCC': 0,
            'is_CC': 0,
            'is_C': 0
        }

    try:
        if value_lambda(internal_score_obj,
                        6,
                        type + '_notch_adjustment') == -1:
            adjustment_liquidity = 'b-'
        else:
            adjustment_liquidity = 0
    except:  # noqa E722
        adjustment_liquidity = 0

    if issuer_type_id == 1:

        # Make dict backwards compatible
        try:
            financial_risk_assessment = {
                'financial_risk_assessment': {
                    'value': value_lambda(internal_score_obj,
                                          5,
                                          type + '_score')
                }
            }
        except IndexError:
            financial_risk_assessment = {
                'ratio_analysis': {
                    'value':
                        value_lambda(internal_score_obj,
                                     27,
                                     type + '_score')
                },
                'risk_appetite':  {
                    'value':
                        value_lambda(internal_score_obj,
                                     28,
                                     type + '_score')
                },
            }

        output = {
            'rating_type': 'corporate',
            'version': version,
            'business_risk_assessment':
                {
                    'operating_environment': {
                        'value': value_lambda(internal_score_obj,
                                              1,
                                              type + '_score'),
                    },
                    'market_position': {
                        'value': value_lambda(internal_score_obj,
                                              2,
                                              type + '_score')
                    },
                    'operating_efficiency': {
                        'value': value_lambda(internal_score_obj,
                                              3,
                                              type + '_score')
                    },
                    'size_diversification': {
                        'value': value_lambda(internal_score_obj,
                                              4,
                                              type + '_score')
                    }
                },
            'financial_risk_assessment': financial_risk_assessment,
            'adjustment_factor': {
                'liquidity': adjustment_liquidity,
                'esg': value_lambda(internal_score_obj,
                                    7,
                                    type + '_notch_adjustment'),
                'peer_comparisons': value_lambda(internal_score_obj,
                                                 8,
                                                 type + '_notch_adjustment')},
            'support': {
                'general': value_lambda(internal_score_obj,
                                        9,
                                        type + '_notch_adjustment')},
            'highest_lowest': highest_lowest,
        }

    elif issuer_type_id == 2:

        output = {
            'rating_type': 'financial',
            'operating_environment':
                {
                    'national_factors': {
                        'value': value_lambda(internal_score_obj,
                                              12,
                                              type + '_score'),
                        'weight': value_lambda(internal_score_obj,
                                               12,
                                               'weight'),
                    },
                    'regional_cross_border_sector_specific': {
                        'value': value_lambda(internal_score_obj,
                                              13,
                                              type + '_score'),
                        'weight': value_lambda(internal_score_obj,
                                               13,
                                               'weight'),
                    }
                },
            'risk_appetite': {
                'capital': {
                    'value': value_lambda(internal_score_obj,
                                          14,
                                          type + '_score'),
                },
                'funding_liquidity': {
                    'value': value_lambda(internal_score_obj,
                                          15,
                                          type + '_score'),
                },
                'risk_governance': {
                    'value': value_lambda(internal_score_obj,
                                          16,
                                          type + '_score'),
                },
                'credit_risk': {
                    'value': value_lambda(internal_score_obj,
                                          17,
                                          type + '_score'),
                    'weight': value_lambda(internal_score_obj,
                                           17,
                                           'weight'),
                },
                'market_risk': {
                    'value': value_lambda(internal_score_obj,
                                          18,
                                          type + '_score'),
                    'weight': value_lambda(internal_score_obj,
                                           18,
                                           'weight'),
                },
                'other_risk': {
                    'value': value_lambda(internal_score_obj,
                                          19,
                                          type + '_score'),
                }},
            'competitive_position': {
                'market_position': {
                    'value': value_lambda(internal_score_obj,
                                          20,
                                          type + '_score'),
                }, },
            'performance_indicator': {
                'earnings': {
                    'value': value_lambda(internal_score_obj,
                                          21,
                                          type + '_score'),
                },
                'loss_performance': {
                    'value': value_lambda(internal_score_obj,
                                          22,
                                          type + '_score'),
                }},
            'adjustment_factor': {
                'transitions':
                    value_lambda(internal_score_obj,
                                 23,
                                 type + '_notch_adjustment'),
                'borderline_assessments':
                    value_lambda(internal_score_obj,
                                 24,
                                 type + '_notch_adjustment'),
                'peer_comparisons':
                    value_lambda(internal_score_obj,
                                 8,
                                 type + '_notch_adjustment'), },
            'support': {
                'ownership':
                    value_lambda(internal_score_obj,
                                 9,
                                 type + '_notch_adjustment'),
                'material_credit_enhancement':
                    value_lambda(internal_score_obj,
                                 25,
                                 type + '_notch_adjustment'),
                'rating_caps':
                    value_lambda(internal_score_obj,
                                 26,
                                 type + '_notch_adjustment'), },
            'highest_lowest': highest_lowest,
        }

    elif issuer_type_id == 3:

        # Make dict backwards compatible
        try:
            financial_risk_assessment = {
                'financial_risk_assessment': {
                    'value': value_lambda(internal_score_obj,
                                          5,
                                          type + '_score')
                }
            }
        except IndexError:
            financial_risk_assessment = {
                'ratio_analysis': {
                    'value':
                        value_lambda(internal_score_obj,
                                     27,
                                     type + '_score')
                },
                'risk_appetite':  {
                    'value':
                        value_lambda(internal_score_obj,
                                     28,
                                     type + '_score')
                },
            }

        output = {
            'rating_type': 'corporate_re',
            'version': version,
            'business_risk_assessment':
                {
                    'operating_environment': {
                        'value': value_lambda(internal_score_obj,
                                              1,
                                              type + '_score'),
                    },
                    'market_position_size_diversification': {
                        'value': value_lambda(internal_score_obj,
                                              10,
                                              type + '_score'),
                    },
                    'operating_efficiency': {
                        'value': value_lambda(internal_score_obj,
                                              3,
                                              type + '_score'),
                    },
                    'portfolio_assessment': {
                        'value': value_lambda(internal_score_obj,
                                              11,
                                              type + '_score'),
                    }
                },
            'financial_risk_assessment': financial_risk_assessment,
            'adjustment_factor': {
                'liquidity': adjustment_liquidity,
                'esg': value_lambda(internal_score_obj,
                                    7,
                                    type + '_notch_adjustment'),
                'peer_comparisons': value_lambda(internal_score_obj,
                                                 8,
                                                 type + '_notch_adjustment')},
            'support': {
                'general': value_lambda(internal_score_obj,
                                        9,
                                        type + '_notch_adjustment')},
            'highest_lowest': highest_lowest,
        }
    else:
        output = 'Not implemented'

    return output
