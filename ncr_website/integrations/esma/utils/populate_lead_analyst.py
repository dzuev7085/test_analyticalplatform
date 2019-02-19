"""Generate data for LeadAnalyst model."""
from integrations.esma.utils.generic import (
    get_or_create_reporting_type_info,
    create_reporting_reason_string,
)
from integrations.esma.utils.hash_functions import create_hash_string
from user_profile.models import LeadAnalyst as OrigModel
from integrations.esma.models.q_lead_analyst import LeadAnalyst as ESMAModel

STRING_NEW_ITEM = 'new lead analyst'

# Change this for the specific model
COMPARE_FIELDS = [
    {
        'field_orig': 'start_date',
        'field_esma': 'lead_analyst_start_date',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'start date change'
    },
    {
        'field_orig': 'end_date',
        'field_esma': 'lead_analyst_end_date',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'end date change'
    },
]


def populate_lead_analyst(xml_file):
    """Scan original model and insert into ESMA model if required.
    This function does a field-by-field comparison against"""

    for orig_record in OrigModel.objects.all():

        # As a default, don't do anything
        change_reason = None
        reporting_type = None
        reporting_reason = []
        create_record = False

        # Unique identifier for this model
        unique_identifier = orig_record.profile.user.username

        try:
            esma_record = ESMAModel.objects.last_valid_record().filter(
                lead_analyst_code=unique_identifier)[0]

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

            # Custom comparison of full name due to the OrigModel
            # being a bit different
            if orig_record.profile.full_name != esma_record.lead_analyst_name:
                create_record = True

                reporting_type = 2  # 2=CHG
                change_reason = 2  # 2=U: Consider this to be an an update
                reporting_reason.append('change of full name')

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

            # Create a new record
            ESMAModel.objects.create(
                xml_file=xml_file,
                reporting_type_info=reporting_type_info,

                # Insert all model fields below here
                lead_analyst_code=unique_identifier,
                lead_analyst_name=orig_record.profile.full_name,
                lead_analyst_start_date=orig_record.start_date,
                lead_analyst_end_date=orig_record.end_date,
            )
