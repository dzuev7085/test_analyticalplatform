"""Generate data for RatingScale model."""
from integrations.esma.utils.generic import (
    get_or_create_reporting_type_info,
    create_reporting_reason_string,
)
from integrations.esma.utils.hash_functions import create_hash_string
from a_helper.static_database_table.models.cra_info import (
    CRAInfo as OrigModel
)
from integrations.esma.models.q_cra_info \
    import CRAInfo as ESMAModel
from gui.templatetags.template_tags import format_reference_number

STRING_NEW_ITEM = 'new CRA info'

# Change this for the specific model
COMPARE_FIELDS = [
    {
        'field_orig': 'cra_name',
        'field_esma': 'cra_name',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'name change'
    },
    {
        'field_orig': 'cra_description',
        'field_esma': 'cra_description',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'description change'
    },
    {
        'field_orig': 'cra_methodology',
        'field_esma': 'cra_methodology',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'methodology change'
    },
    {
        'field_orig': 'cra_methodology_webpage_link',
        'field_esma': 'cra_methodology_webpage_link',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'methodology link'
    },
    {
        'field_orig': 'solicited_unsolicited_rating_policy_description',
        'field_esma': 'solicited_unsolicited_rating_policy_description',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'solicited/unsolicited description'
    },
    {
        'field_orig': 'subsidiary_rating_policy',
        'field_esma': 'subsidiary_rating_policy',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'subsidiary rating policy'
    },
    {
        'field_orig': 'global_reporting_scope_flag',
        'field_esma': 'global_reporting_scope_flag',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'global reporting flag'
    },
    {
        'field_orig': 'definition_default',
        'field_esma': 'definition_default',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'definition default'
    },
    {
        'field_orig': 'cra_website_link',
        'field_esma': 'cra_website_link',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'web site link'
    },

]


def populate_cra_info(xml_file):
    """Scan original model and insert into ESMA model if required.
    This function does a field-by-field comparison against"""

    for orig_record in OrigModel.objects.all():

        # As a default, don't do anything
        change_reason = None
        reporting_type = None
        reporting_reason = []
        create_record = False

        # Unique identifier for this model
        unique_identifier = format_reference_number(
            object_type='cra_info',
            number=orig_record.id)

        try:
            esma_record = ESMAModel.objects.last_valid_record()[0]

            for compare_obj in COMPARE_FIELDS:

                """Compare value of field in base model with ESMA record."""
                if (getattr(orig_record, compare_obj['field_orig']) !=
                        getattr(esma_record, compare_obj['field_esma'])):

                    # Something has changed, create a new entry in ESMA-table.
                    create_record = True

                    reporting_type = compare_obj['reporting_type']
                    change_reason = compare_obj['change_reason']
                    reporting_reason.append(
                        compare_obj['reporting_reason'])

        except (IndexError, ESMAModel.DoesNotExist):
            """The object is not existing in the ESMA table:
            create it."""

            create_record = True
            reporting_type = 1  # 1=NEW
            reporting_reason.append(STRING_NEW_ITEM)

        if create_record:
            # Create a new ReportingTypeInfo record
            reporting_type_info, _ = get_or_create_reporting_type_info(
                reporting_type=reporting_type,
                change_reason=change_reason,
                reporting_reason_text=create_reporting_reason_string(
                    reporting_reason),
                hash_string=create_hash_string(
                    unique_identifier,
                    reporting_type)
            )

            # Because of the long variable name
            a = orig_record.\
                solicited_unsolicited_rating_policy_description

            # Create a new record
            ESMAModel.objects.create(
                xml_file=xml_file,
                reporting_type_info=reporting_type_info,

                # Insert all model fields below here
                cra_info_code=unique_identifier,
                cra_name=orig_record.cra_name,
                cra_description=orig_record.cra_description,
                cra_methodology=orig_record.cra_methodology,
                cra_methodology_webpage_link=orig_record.
                cra_methodology_webpage_link,
                solicited_unsolicited_rating_policy_description=a,
                subsidiary_rating_policy=orig_record.
                subsidiary_rating_policy,
                global_reporting_scope_flag=orig_record.
                global_reporting_scope_flag,
                definition_default=orig_record.definition_default,
                cra_website_link=orig_record.cra_website_link,
            )
