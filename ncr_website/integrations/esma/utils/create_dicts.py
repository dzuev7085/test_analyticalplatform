"""Return dicts that are passed to the XML creator.

This file should not contain any logic, only fetch data from the databases."""
from integrations.esma.models.q_cra_info import CRAInfo
from integrations.esma.models.q_lead_analyst import LeadAnalyst
from integrations.esma.models.q_debt_classification import DebtClassification
from integrations.esma.models.q_issue_program import IssueProgram
from integrations.esma.models.q_issuer_rating import IssuerRating
from integrations.esma.models.q_rating_scale import (
    RatingScale,
    RatingScope,
    RatingCategory,
    RatingNotch
)
from integrations.esma.models.qt_rating_action import QTRatingCreateData
from issue.models import SeniorityLevel
from pyesmaradar import attachment_file_name
from django.conf import settings
from ..const import YN_MAPPING, YN_MAPPING_REVERSE


def reporting_type_info(record):
    """Return dict for reporting type info."""

    reporting_type = record.reporting_type_info. \
        get_reporting_type_display()

    if reporting_type == 'NEW' or reporting_type == 'CHG':
        update_date = ''
    else:
        update_date = record.insertion_date.strftime('%Y-%m-%d')

    REPORTING_TYPE_INFO = {
        'reporting_type':
            reporting_type,
        'change_reason':
            record.reporting_type_info.get_change_reason_display(),
        'reporting_reason':
            record.reporting_type_info.reporting_reason,
        'update_date':
            update_date
    }

    return REPORTING_TYPE_INFO


def return_lead_analyst_list(xml_file):
    """return a list of dicts contaning lead analyst information
    in the format required by the NCR->ESMA XML parser."""

    OUTPUT_LIST = []

    try:
        for record in LeadAnalyst.objects.filter(xml_file=xml_file):

            row = {}
            row_data = {
                'reporting_type_info': reporting_type_info(record),
                'lead_analyst_code':
                    record.lead_analyst_code,
                'lead_analyst_name':
                    record.lead_analyst_name,
                'lead_analyst_start_date':
                    record.lead_analyst_start_date.strftime('%Y-%m-%d'),
                'lead_analyst_end_date':
                    record.lead_analyst_end_date.strftime('%Y-%m-%d'),
            }

            row['lead_analyst'] = row_data

            OUTPUT_LIST.append(row)

        return OUTPUT_LIST
    except LeadAnalyst.DoesNotExist:

        return False


def return_debt_classification_list(xml_file):
    """return a list of dicts contaning debt classification information
    in the format required by the NCR->ESMA XML parser."""

    OUTPUT_LIST = []

    try:
        for record in DebtClassification.objects.filter(xml_file=xml_file):

            row = {}
            row_data = {
                'reporting_type_info': reporting_type_info(record),
                'debt_classification_code':
                    record.debt_classification_code,
                'debt_classification_name':
                    record.debt_classification_name,
                'debt_classification_description':
                    record.debt_classification_description,
                'debt_classification_start_date':
                    record.debt_classification_start_date.strftime('%Y-%m-%d'),
                'seniority':
                    SeniorityLevel.objects.get(pk=record.seniority).name,
                'debt_classification_end_date':
                    record.debt_classification_end_date.strftime('%Y-%m-%d'),
            }

            row['rated_debt_classification'] = row_data

            OUTPUT_LIST.append(row)

        return OUTPUT_LIST

    except DebtClassification.DoesNotExist:

        return False


def return_issue_program_list(xml_file):
    """return a list of dicts contaning debt classification information
    in the format required by the NCR->ESMA XML parser."""

    OUTPUT_LIST = []

    try:
        for record in IssueProgram.objects.filter(xml_file=xml_file):

            row = {}
            row_data = {
                'reporting_type_info': reporting_type_info(record),
                'issue_program_code':
                    record.program_code,
                'issue_program_name':
                    record.program_name,
                'issue_program_description':
                    record.program_description,
                'issue_program_start_date':
                    record.program_start_date.strftime('%Y-%m-%d'),
                'issue_program_end_date':
                    record.program_end_date.strftime('%Y-%m-%d'),
            }

            row['issue_program'] = row_data

            OUTPUT_LIST.append(row)

        return OUTPUT_LIST

    except IssueProgram.DoesNotExist:

        return False


def return_issuer_rating_list(xml_file):
    """return a list of dicts contaning debt classification information
    in the format required by the NCR->ESMA XML parser."""

    OUTPUT_LIST = []

    try:
        for record in IssuerRating.objects.filter(xml_file=xml_file):

            row = {}
            row_data = {
                'reporting_type_info': reporting_type_info(record),
                'issuer_rating_type_code':
                    record.rating_type_code,
                'issuer_rating_type_name':
                    record.rating_type_name,
                'issuer_rating_type_description':
                    record.rating_type_description,
                'issuer_rating_type_standard':
                    record.get_rating_type_standard_display(),
                'issuer_rating_type_start_date':
                    record.rating_type_start_date.strftime('%Y-%m-%d'),
                'issuer_rating_type_end_date':
                    record.rating_type_end_date.strftime('%Y-%m-%d'),
            }

            row['issuer_rating_info'] = row_data

            OUTPUT_LIST.append(row)

        return OUTPUT_LIST
    except IssuerRating.DoesNotExist:

        return False


def return_rating_scale_list(xml_file):
    """return a list of dicts rating scale information
    in the format required by the NCR->ESMA XML parser."""

    OUTPUT_LIST = []

    try:
        for record in RatingScale.objects.filter(
                xml_file=xml_file).order_by('id'):

            SCOPE_LIST = []
            for scope_record in RatingScope.objects.filter(
                    rating_scale=record).order_by('id'):

                scope_row = {
                    'scope': {
                        'time_horizon':
                            scope_record.get_time_horizon_display(),
                        'rating_type':
                            scope_record.get_rating_type_display(),
                        'rating_scale_scope':
                            scope_record.get_rating_scale_scope_display(),
                        'relevant_for_cerep_flag':
                            YN_MAPPING[scope_record.relevant_for_cerep_flag],
                        'scope_start_date':
                            scope_record.start_date.strftime('%Y-%m-%d'),
                        'scope_end_date':
                            scope_record.end_date.strftime('%Y-%m-%d'),
                    }
                }
                SCOPE_LIST.append(scope_row)

            CATEGORY_LIST = []
            for category_record in RatingCategory.objects.filter(
                    rating_scale=record).order_by('id'):

                NOTCH = []
                for notch_record in RatingNotch.objects.filter(
                        rating_category=category_record).order_by('id'):
                    notch_row = {
                        'notch': {
                            'notch_value': str(notch_record.value),
                            'notch_label': notch_record.label,
                            'notch_description': notch_record.description,
                        }
                    }
                    NOTCH.append(notch_row)

                category_row = {
                    'category_value': str(category_record.value),
                    'category_label': category_record.label,
                    'category_description': category_record.description,
                    'notch_list': NOTCH
                }
                CATEGORY_LIST.append(category_row)

            row = {}
            row_data = {
                'reporting_type_info': reporting_type_info(record),
                'rating_scale_code':
                    record.rating_scale_code,
                'rating_scale_start_date':
                    record.start_date.strftime('%Y-%m-%d'),
                'rating_scale_end_date':
                    record.end_date.strftime('%Y-%m-%d'),
                'rating_scale_description':
                    record.description,
                'scope_list':
                    SCOPE_LIST,
                'category_list':
                    CATEGORY_LIST
            }

            row['rating_scale'] = row_data

            OUTPUT_LIST.append(row)

        return OUTPUT_LIST

    except RatingScale.DoesNotExist:

        return False


def return_cra_info(xml_file):
    """Return CRA info in the format required by the
    NCR->ESMA XML parser."""

    try:
        record = CRAInfo.objects.get(xml_file=xml_file)

        return ({
            'reporting_type_info': reporting_type_info(record),
            'cra_name': record.cra_name,
            'cra_description': record.cra_description,
            'cra_methodology': record.cra_methodology,
            'cra_methodology_webpage_link':
                record.cra_methodology_webpage_link,
            'solicited_unsolicited_rating_policy_description':
                record.solicited_unsolicited_rating_policy_description,
            'subsidiary_rating_policy': record.subsidiary_rating_policy,
            'geographical_reporting_scope': {
                'global_reporting_scope_flag':
                    str(YN_MAPPING_REVERSE[
                            record.get_global_reporting_scope_flag_display()]
                        ).lower()
            },
            'definition_default': record.definition_default,
            'cra_website_link': record.cra_website_link
        })

    except CRAInfo.DoesNotExist:

        return False


def return_rating_quantitative(xml_file):
    """Return dict for a rating action."""

    try:
        r = QTRatingCreateData.objects.get(xml_file=xml_file)

        RESEARCH_REPORT = {}
        PRESS_RELEASE = {}
        RATING_INFO = {}

        # Unique id for this rating. Must remain the same over time
        rating_action_identifier = r.rating_action_identifier

        rating_job_id = r.rating_identifier_formatted

        # Only populate if the previous decision was a preliminary
        if r.qtratingaction.qtratinginfo.qtprecedingpreliminaryrating.\
                preliminary_rating_identifier is not None:
                preceding_preliminary_rating_identifier = (
                    r.qtratingaction.qtratinginfo.
                    qtprecedingpreliminaryrating.
                    preliminary_rating_identifier)
        else:
            preceding_preliminary_rating_identifier = None

        # Upgrade, downgrade, affirmation etc
        action_type = r.qtratingaction.get_action_type_display()

        if r.qtratingaction.qtratinginfo.type_of_rating_for_erp == 1:
            RESEARCH_REPORT = {
                'research_report_language': 'en',  # Hard coded for now
                'research_report_file_name': attachment_file_name(
                    sender=settings.ESMA_CRA_CODE,
                    file_type='RRR',
                    rating_action_id=rating_action_identifier,
                    rating_identifier=rating_job_id,
                    language='en',
                    file_format='',
                    include_file_type=False,
                ),
                'link_to_rating_action_identifier': ''  # Not required
            }

            PRESS_RELEASE = {
                'press_release_language': 'en',  # Hard coded for now
                'press_release_file_name': attachment_file_name(
                    sender=settings.ESMA_CRA_CODE,
                    file_type='PPR',
                    rating_action_id=rating_action_identifier,
                    rating_identifier=rating_job_id,
                    language='en',
                    file_format='',
                    include_file_type=False,
                ),
                'link_to_rating_action_identifier': ''  # Not required
            }

        ISSUER_INFO = {
            'issuer_lei_code':
                r.qtratingaction.qtratinginfo.
                qtissuerinfo.lei_code,
            'issuer_internal_code':
                r.qtratingaction.qtratinginfo.
                qtissuerinfo.issuer_internal_code,
            'issuer_name':
                r.qtratingaction.qtratinginfo.
                qtissuerinfo.issuer_name
        }

        PRECEDING_PRELIMINARY_RATING = {
            'preceding_preliminary_rating_flag':
                YN_MAPPING[
                    r.qtratingaction.qtratinginfo.
                    qtprecedingpreliminaryrating.
                    preceding_preliminary_rating_flag],
            'preceding_preliminary_rating_identifier':
                preceding_preliminary_rating_identifier,
        }

        if action_type in ['PR', 'OR', 'NW']:
            RATING_INFO = {
                'responsible_cra_lei':
                    r.qtratingaction.qtratinginfo.responsible_cra_lei,
                'issuer_cra_lei':
                    r.qtratingaction.qtratinginfo.issuer_cra_lei,
                'rating_type':
                    r.qtratingaction.qtratinginfo.get_rating_type_display(),
                'other_rating_type':
                    r.qtratingaction.qtratinginfo.other_rating_type,
                'rated_object':
                    r.qtratingaction.qtratinginfo.get_rated_object_display(),
                'time_horizon':
                    r.qtratingaction.qtratinginfo.get_time_horizon_display(),
                'country':
                    r.qtratingaction.qtratinginfo.country,
                'local_foreign_currency':
                    r.qtratingaction.qtratinginfo.
                    get_local_foreign_currency_display(),
                'issuer_info': ISSUER_INFO,

                # Will be None if reporting an issue
                'issuer_rating_type_code':
                    r.qtratingaction.qtratinginfo.issuer_rating_type_code,

                # Will be None if reporting an issuer
                'debt_classification_code':
                    r.qtratingaction.qtratinginfo.debt_classification_code,
                'industry': r.qtratingaction.qtratinginfo.
                    get_industry_display(),

                # Applicable only in case the rating type reported is “S”.
                'sector':
                    r.qtratingaction.qtratinginfo.sector,

                # Applicable only in case the rating type reported is “T”.
                'asset_class':
                    r.qtratingaction.qtratinginfo.asset_class,

                # Applicable only in case the rating type reported is “T”.
                'sub_asset':
                    r.qtratingaction.qtratinginfo.sub_asset,

                # Applicable only in case the rating type reported is “T”.
                'other_sub_asset':
                    r.qtratingaction.qtratinginfo.other_sub_asset,

                'type_of_rating_for_erp':
                    r.qtratingaction.qtratinginfo.
                    get_type_of_rating_for_erp_display(),
                'relevant_for_cerep_flag':
                    YN_MAPPING[
                        r.qtratingaction.qtratinginfo.relevant_for_cerep],
                'preceding_preliminary_rating_info':
                    PRECEDING_PRELIMINARY_RATING, }

        RATING_ACTION_DATA = {
            'action_type': action_type,
            'rating_value_info': {
                'rating_value':
                    r.qtratingaction.qtratingvalue.rating_value,
                'rating_scale_code':
                    r.qtratingaction.qtratingvalue.rating_scale_code,
                'default_flag':
                    YN_MAPPING[
                        r.qtratingaction.qtratingvalue.default_flag], },
            'rating_info': RATING_INFO,
            'owsd_status': r.qtratingaction.get_owsd_status_display(),
            'outlook_trend': r.qtratingaction.get_outlook_trend_display(),
            'watch_review': r.qtratingaction.get_watch_review_display(),
            'withdrawal_reason_type':
                r.qtratingaction.get_withdrawal_reason_type_display(),
        }

        try:
            if r.qtratingaction.qtratinginfo.qtinstrumentinfo:
                RATING_INFO.update({'instrument_info': {
                    'instrument_isin_code':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        isin_code,
                    'instrument_internal_code':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        instrument_internal_code,
                    'instrument_unique_identifier':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        instrument_unique_identifier,
                    'issuance_date':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        issuance_date,
                    'maturity_date':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        maturity_date,
                    'outstanding_issue_volume':
                        int(r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                            outstanding_issue_volume),
                    'issue_volume_currency_code':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        issue_volume_currency_code,
                    'program_deal_issuance_name':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        program_deal_issuance_name,
                    'corporate_issue_classification':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        get_corporate_issue_classification_display(),
                    'other_corporate_issues':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        other_corporate_issues,
                    'issue_program_code':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        issue_program_code,
                    'tranche_class':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        tranche_class,
                    'serie_program_code':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        serie_program_code,
                    'originator_info_list': '',  # strf only
                    'complexity_indicator':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        complexity_indicator,
                    'structured_finance_transaction_type':
                        r.qtratingaction.qtratinginfo.qtinstrumentinfo.
                        structured_finance_transaction_type
                }})
        except:  # noqa: E722
            pass

        OUTPUT = {
            'rating_create_data':
                {
                    'reporting_type': r.get_reporting_type_display(),
                    'rating_action_identifier': rating_action_identifier,
                    'rating_job_id': rating_job_id,
                    'rating_action_info':
                        {
                            'rating_issuance_location':
                                r.qtratingactioninfo.
                                get_rating_issuance_location_display(),
                            'action_date_info': {
                                'communication_date':
                                    r.qtratingactioninfo.qtactiondateinfo.
                                    communication_date.isoformat(),
                                'decision_date':
                                    r.qtratingactioninfo.qtactiondateinfo.
                                    decision_date.date(),
                                'validity_date':
                                    r.qtratingactioninfo.qtactiondateinfo.
                                    validity_date.isoformat()},
                            'lead_analyst_info': {
                                'lead_analyst_code':
                                    r.qtratingactioninfo.
                                    qtleadanalystinfo.lead_analyst_code,
                                'lead_analyst_country_code':
                                    r.qtratingactioninfo.qtleadanalystinfo.
                                    lead_analyst_country_code, },
                            'rating_data_solicited_unsolicited':
                                r.qtratingactioninfo.
                                get_rating_solicited_unsolicited_display(),
                            'press_release_flag':
                                YN_MAPPING[
                                    r.qtratingactioninfo.press_release_flag],
                            'press_release': PRESS_RELEASE,
                            'research_report_flag':
                                YN_MAPPING[
                                    r.qtratingactioninfo.research_report_flag],
                            'research_report': RESEARCH_REPORT,
                        },
                    'rating_action': RATING_ACTION_DATA,
                }}

        return OUTPUT

    except QTRatingCreateData.DoesNotExist:

        return False
