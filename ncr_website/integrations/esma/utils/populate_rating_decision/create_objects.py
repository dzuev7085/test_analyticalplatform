"""This module creates all objects that back the XML files."""
from celery.utils.log import get_task_logger
from integrations.esma.models.xml_file import XMLFile
from integrations.esma.models.qt_rating_action import (
    QTRatingCreateData,
    QTRatingActionInfo,
    QTActionDateInfo,
    QTLeadAnalystInfo,
    QTRatingAction,
    QTRatingValue,
    QTRatingInfo,
    QTIssuerInfo,
    QTPrecedingPreliminaryRating,
    QTInstrumentInfo,
)
from integrations.esma.const import (
    NCR_LEI,
    FILE_TYPE_RATING_QUANTITATIVE,
    FILE_TYPE_LOOKUP,
)
from gui.templatetags.template_tags import format_reference_number
from integrations.esma.utils.populate_rating_decision.helpers import (
    press_release_data,
    research_report_data
)

logger = get_task_logger(__name__)


def create_rating_decision_xml_objects(hash_key,
                                       dec,
                                       x,
                                       validity_date,
                                       t,
                                       owsd_status,
                                       outlook_trend,
                                       watch_review,
                                       withdrawal_reason_type,
                                       rating_scale_id,
                                       rating_value,
                                       default_flag,
                                       rated_object,
                                       perspective,
                                       issuer_rating_type_code,
                                       debt_classification_code,
                                       industry,
                                       type_of_rating_for_erp,
                                       relevant_for_cerep,
                                       prev_rating_preliminary,
                                       issues,
                                       iss,
                                       attributes,):

    # Get data needed to send the external research report and press release
    # if applicable
    # - is_between_committees is set when an issue rating has been
    # decided between regular rating committees
    # - is_matured is set on the maturity date of an issue
    if issues and (attributes.is_between_committees or attributes.is_matured):
        research_report = None
        research_report_flag = False

        press_release = None
        press_release_flag = False
    else:
        press_release, press_release_flag = press_release_data(dec)
        research_report, research_report_flag = research_report_data(dec)

    xml_file = XMLFile.objects.create(
        file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUANTITATIVE]
    )
    logger.info("               created XML")

    rating_create_data = QTRatingCreateData.objects.create(
        # Link to XML file
        xml_file=xml_file,

        # Unique for this record
        hash=hash_key,

        # Reference the rating decision
        rating_decision=dec,

        # Only allowed value here is NEW
        reporting_type=1,

        # Number that follows the rating through its life time
        rating_identifier=dec.esma_rating_identifier,
    )
    logger.info("               created RatingCreateData")

    rating_action_info = QTRatingActionInfo.objects.create(
        # Link to parent object
        rating_create_data=rating_create_data,

        # Always 1=I: Issued in the Union
        rating_issuance_location=1,

        # Always 1=S: Solicited
        rating_solicited_unsolicited=1,

        # True if there is a press release
        press_release_flag=press_release_flag,

        # Link to model
        press_release=press_release,

        # True if there is a research report
        research_report_flag=research_report_flag,

        # Link to research report
        research_report=research_report,
    )
    logger.info("               created RatingActionInfo")

    QTActionDateInfo.objects.create(
        # Link to parent
        rating_action_info=rating_action_info,

        # Time stamp of committee
        decision_date=x.date_time_committee,

        # Time stamp when the draft decision was sent to
        # the issuer
        communication_date=x.date_time_communicated_issuer,

        # Time stamp when the rating was published
        validity_date=validity_date,
    )
    logger.info("               created ActionDateInfo")

    QTLeadAnalystInfo.objects.create(
        # Link to parent
        rating_action_info=rating_action_info,

        # Link to a CountryRegion object
        country_model=dec.primary_analyst.profile.office_location,

        # NCR code of user, eg sg06
        lead_analyst_code=dec.primary_analyst.username,
    )
    logger.info("               created LeadAnalystInfo")

    rating_action = QTRatingAction.objects.create(
        # Link to parent
        rating_create_data=rating_create_data,

        # Preliminary, new rating etc
        action_type=t,

        owsd_status=owsd_status,
        outlook_trend=outlook_trend,
        watch_review=watch_review,
        withdrawal_reason_type=withdrawal_reason_type,
    )
    logger.info("               created RatingAction")

    # 10 = outlook change, we don't need this info then
    QTRatingValue.objects.create(
        # Link to parent
        rating_action=rating_action,

        # Depending on short-term/long-term
        # and if preliminary or not
        rating_scale_id=rating_scale_id,

        # Depending on type of rating
        rating_value=rating_value,

        # In default?
        default_flag=default_flag,
    )
    logger.info("               created RatingValue")

    rating_info = QTRatingInfo.objects.create(
        rating_action=rating_action,  # Link to parent

        # Country of the rated entity or issue
        country_model=dec.issuer.address.country,

        # LEI code of Nordic Credit Rating
        responsible_cra_lei=NCR_LEI,

        # LEI code of Nordic Rredit Rating
        issuer_cra_lei=NCR_LEI,

        # Hardcoded to 1=C:corporate for now
        rating_type=1,

        # Not in use
        other_rating_type=None,

        # Issuer or issue
        rated_object=rated_object,

        # Long-term or short-term
        time_horizon=perspective,

        # Value discussed and decided with ESMA
        # to be foreign
        local_foreign_currency=2,  # 2=Foreign

        issuer_rating_type_code=issuer_rating_type_code,
        debt_classification_code=debt_classification_code,

        # FI or Corporate
        industry=industry,

        # Not in use
        sector=None,

        # Not in use,
        asset_class=None,

        # Not in use,
        sub_asset=None,

        # Whether produced for a fee or not
        type_of_rating_for_erp=type_of_rating_for_erp,

        # Published on CEREP?
        relevant_for_cerep=relevant_for_cerep,
    )
    logger.info("               created RatingInfo")

    QTPrecedingPreliminaryRating.objects.create(
        rating_info=rating_info,
        preceding_preliminary_rating_flag=prev_rating_preliminary,
    )
    logger.info("               created "
                "PrecedingPreliminaryRating")

    QTIssuerInfo.objects.create(
        rating_info=rating_info,  # Link to parent

        lei_code=dec.issuer.lei,
        issuer_name=dec.issuer.legal_name,
    )
    logger.info("               created IssuerInfo")

    if issues:
        QTInstrumentInfo.objects.create(
            rating_info=rating_info,

            issue=iss.issue,
            isin_code=iss.issue.isin,

            # Currently not in use according to specs
            instrument_unique_identifier=None,

            issuance_date=iss.issue.disbursement,
            maturity_date=iss.issue.maturity,
            outstanding_issue_volume=iss.issue.amount,
            currency=iss.issue.currency,

            program_deal_issuance_name=iss.issue.program.name,

            # TODO: later on add support for covered bonds
            corporate_issue_classification=1,

            # Not relevant
            other_corporate_issues=None,

            issue_program_code=format_reference_number(
                number=iss.issue.program.pk,
                object_type='issue_program'),

            # Assumed structured finance only
            tranche_class=None,

            # Assumed structured finance only
            serie_program_code=None,

            # Assumed structured finance only
            complexity_indicator=None,

            # Assumed structured finance only
            structured_finance_transaction_type=None,
        )
        logger.info("               created InstrumentInfo")
