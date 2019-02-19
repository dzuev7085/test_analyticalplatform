"""Generate data for RatingScale model."""
from integrations.esma.utils.generic import (
    get_or_create_reporting_type_info,
    create_reporting_reason_string,
)
from integrations.esma.utils.hash_functions import create_hash_string
from issue.models import Seniority as OrigModel
from integrations.esma.models.q_debt_classification import (
    DebtClassification as ESMAModel
)
from gui.templatetags.template_tags import format_reference_number

STRING_NEW_ITEM = 'new debt classification'

# Change this for the specific model
COMPARE_FIELDS = [
    {
        'field_orig': 'start_date',
        'field_esma': 'debt_classification_start_date',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'start date'
    },
    {
        'field_orig': 'end_date',
        'field_esma': 'debt_classification_end_date',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'end date'
    },
    {
        'field_orig': 'description',
        'field_esma': 'debt_classification_description',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'description'
    },
    {
        'field_orig': 'name',
        'field_esma': 'debt_classification_name',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'name'
    },
]


def populate_debt_classification(xml_file):
    """Scan original model and insert into ESMA model if required."""

    for orig_record in OrigModel.objects.all():

        # As a default, don't do anything
        change_reason = None
        reporting_type = None
        reporting_reason = []
        create_record = False

        # Unique identifier for this model
        unique_identifier = format_reference_number(
            object_type='debt_class',
            number=orig_record.id)

        try:
            esma_record = ESMAModel.objects.last_valid_record().filter(
                debt_classification_code=unique_identifier)[0]

            for compare_obj in COMPARE_FIELDS:

                """Compare value of field in base model with ESMA record."""
                if (getattr(orig_record, compare_obj['field_orig']) !=
                        getattr(esma_record, compare_obj['field_esma'])):

                    create_record = True

                    reporting_type = compare_obj['reporting_type']
                    change_reason = compare_obj['change_reason']
                    reporting_reason.append(
                        compare_obj['reporting_reason'])

            # Custom comparison of seniority due to the OrigModel
            # being a bit different
            if orig_record.seniority_level.id != esma_record.seniority:
                create_record = True

                reporting_type = 2  # 2=CHG
                change_reason = 1  # 2=U: Consider this to be an an update
                reporting_reason.append('seniority level')

        except (IndexError, ESMAModel.DoesNotExist):
            """The rating scale is not existing in the ESMA table,
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
                debt_classification_code=unique_identifier,
                debt_classification_name=orig_record.name,
                debt_classification_description=orig_record.description,
                seniority=orig_record.seniority_level.id,
                debt_classification_start_date=orig_record.start_date,
                debt_classification_end_date=orig_record.end_date,
            )
