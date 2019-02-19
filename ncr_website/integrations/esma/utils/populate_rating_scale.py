"""Generate data for RatingScale model."""
from integrations.esma.utils.generic import (
    get_or_create_reporting_type_info,
    create_reporting_reason_string,
)
from integrations.esma.utils.hash_functions import create_hash_string
from a_helper.static_database_table.models.rating_scale import (
    RatingScale as RatingScaleOrig,
    RatingScope as RatingScopeOrig,
    RatingCategory as RatingCategoryOrig,
    RatingNotch as RatingNotchOrig,
)
from integrations.esma.models.q_rating_scale import (
    RatingScale as RatingScaleESMA,
    RatingScope as RatingScopeESMA,
    RatingCategory as RatingCategoryESMA,
    RatingNotch as RatingNotchESMA

)
from gui.templatetags.template_tags import format_reference_number

STRING_NEW_ITEM = 'new rating scale'

# Change this for the specific model
RSCALE_COMPARE_FIELDS = [
    {
        'field_orig': 'start_date',
        'field_esma': 'start_date',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating scale start date'
    },
    {
        'field_orig': 'end_date',
        'field_esma': 'end_date',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'rating scale end date'
    },
    {
        'field_orig': 'description',
        'field_esma': 'description',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'rating scale description'
    },
]

RSCOPE_COMPARE_FIELDS = [
    {
        'field_orig': 'time_horizon',
        'field_esma': 'time_horizon',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating scope time horizon'
    },
    {
        'field_orig': 'rating_type',
        'field_esma': 'rating_type',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating type'
    },
    {
        'field_orig': 'rating_scale_scope',
        'field_esma': 'rating_scale_scope',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating scope rating scale scope'
    },
    {
        'field_orig': 'relevant_for_cerep_flag',
        'field_esma': 'relevant_for_cerep_flag',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating scope relevant for CEREP flag'
    },
    {
        'field_orig': 'start_date',
        'field_esma': 'start_date',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating scope start date'
    },
    {
        'field_orig': 'end_date',
        'field_esma': 'end_date',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'rating scope end date'
    },
]

RCATEGORY_COMPARE_FIELDS = [
    {
        'field_orig': 'value',
        'field_esma': 'value',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating category value'
    },
    {
        'field_orig': 'label',
        'field_esma': 'label',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating category label'
    },
    {
        'field_orig': 'description',
        'field_esma': 'description',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'rating category description'
    },
]

RNOTCH_COMPARE_FIELDS = [
    {
        'field_orig': 'value',
        'field_esma': 'value',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating notch value'
    },
    {
        'field_orig': 'label',
        'field_esma': 'label',
        'reporting_type': 2,
        'change_reason': 1,
        'reporting_reason': 'rating notch label'
    },
    {
        'field_orig': 'description',
        'field_esma': 'description',
        'reporting_type': 2,
        'change_reason': 2,
        'reporting_reason': 'rating notch description'
    },
]


def populate_rating_scale(xml_file):
    """Scan original model and return change reason as well as change type."""

    create_record = False
    esma_record = None

    create_or_update_id = []

    reporting_reason_dict = {}
    reporting_type_dict = {}
    change_reason_dict = {}

    """Rating scale."""
    for rating_scale in RatingScaleOrig.objects.order_by('id').all():

        """Do a field by field comparison"""
        # Unique identifier for this model
        unique_identifier_rating_scale = format_reference_number(
            object_type='rating_scale',
            number=rating_scale.id)

        try:
            esma_record = RatingScaleESMA.objects.filter(
                rating_scale_code=unique_identifier_rating_scale,
                xml_file__status_code=1).order_by('-id').all()[0]

        except (IndexError, RatingScaleESMA.DoesNotExist):
            """There is no record in the ESMA model, create it."""

            create_record = True

            # Create a list of IDs that should be inserted
            create_or_update_id.append(rating_scale.id)

            reporting_type_dict[rating_scale.id] = 1  # 1=NEW

            # must be list
            reporting_reason_dict[rating_scale.id] = [STRING_NEW_ITEM]

        if not create_record:
            """There is an existing parent, check for differences and if
            differences, generate change reason and change."""

            reporting_reason_dict[rating_scale.id] = []

            for compare_obj in RSCALE_COMPARE_FIELDS:

                """Compare value of field in base model with ESMA record."""
                if (getattr(rating_scale, compare_obj['field_orig']) !=
                        getattr(esma_record, compare_obj['field_esma'])):

                    create_or_update_id.append(rating_scale.id)

                    reporting_type_dict[
                        rating_scale.id] = compare_obj[
                        'reporting_type']
                    change_reason_dict[
                        rating_scale.id] = compare_obj['change_reason']
                    reporting_reason_dict[
                        rating_scale.id].append(
                        compare_obj['reporting_reason'])

            """Scope."""
            for orig_scope_record in RatingScopeOrig.objects.filter(
                    rating_scale=rating_scale).order_by('-id').all():

                unique_identifier_rating_scope = format_reference_number(
                    object_type='rating_scope',
                    number=orig_scope_record.id)

                esma_record_scope = RatingScopeESMA.objects.filter(
                    rating_scope_code=unique_identifier_rating_scope
                ).order_by('-id')[0]

                for compare_obj in RSCOPE_COMPARE_FIELDS:

                    """Compare value of field in base model with
                    ESMA record."""
                    if (getattr(orig_scope_record,
                                compare_obj['field_orig']) !=
                        getattr(esma_record_scope,
                                compare_obj['field_esma'])):

                        # Should be top level id
                        create_or_update_id.append(rating_scale.id)

                        reporting_type_dict[
                            rating_scale.id
                        ] = compare_obj[
                            'reporting_type']
                        change_reason_dict[
                            rating_scale.id
                        ] = compare_obj['change_reason']
                        reporting_reason_dict[rating_scale.id].append(
                            compare_obj['reporting_reason'])

            """Category."""
            for orig_category_record in RatingCategoryOrig.objects.filter(
                    rating_scale=rating_scale).order_by('-id').all():

                unique_identifier_rating_category = format_reference_number(
                    object_type='rating_category',
                    number=orig_category_record.id)

                esma_record_category = RatingCategoryESMA.objects.filter(
                    rating_category_code=unique_identifier_rating_category
                ).order_by('-id')[0]

                for compare_obj in RCATEGORY_COMPARE_FIELDS:

                    """Compare value of field in base model with ESMA
                    record."""
                    if (getattr(orig_category_record,
                                compare_obj['field_orig']) !=
                        getattr(esma_record_category,
                                compare_obj['field_esma'])):

                        # Should be top level id
                        create_or_update_id.append(rating_scale.id)

                        reporting_type_dict[
                            rating_scale.id
                        ] = compare_obj[
                            'reporting_type']
                        change_reason_dict[
                            rating_scale.id
                        ] = compare_obj['change_reason']
                        reporting_reason_dict[rating_scale.id].append(
                            compare_obj['reporting_reason'])

                    """Notch."""
                    for orig_notch_record in RatingNotchOrig.objects.filter(
                        rating_category=orig_category_record
                    ).order_by('-id').all():

                        unique_identifier_rating_notch = \
                            format_reference_number(
                                object_type='rating_notch',
                                number=orig_notch_record.id)

                        esma_record_notch = RatingNotchESMA.objects.filter(
                            rating_notch_code=unique_identifier_rating_notch
                        ).order_by('-id')[0]

                        for compare_obj in RNOTCH_COMPARE_FIELDS:

                            """Compare value of field in base model with
                            ESMA record."""
                            if (getattr(orig_notch_record,
                                        compare_obj['field_orig']) !=
                                getattr(esma_record_notch,
                                        compare_obj['field_esma'])):

                                # Should be top level id
                                create_or_update_id.append(rating_scale.id)

                                reporting_type_dict[
                                    rating_scale.id] = compare_obj[
                                    'reporting_type']
                                change_reason_dict[
                                    rating_scale.id
                                ] = compare_obj['change_reason']
                                reporting_reason_dict[rating_scale.id].append(
                                    compare_obj['reporting_reason'])

            # Looks like nothing happened with this record, delete it
            if len(reporting_reason_dict[rating_scale.id]) == 0:
                del reporting_reason_dict[rating_scale.id]

    for rating_scale_orig in RatingScaleOrig.objects.filter(
            pk__in=create_or_update_id).all():

        reporting_type = reporting_type_dict[rating_scale_orig.id]
        reporting_reason = reporting_reason_dict[rating_scale_orig.id]

        try:
            change_reason = change_reason_dict[rating_scale_orig.id]
        except KeyError:
            change_reason = None

        unique_identifier_rating_scale = format_reference_number(
            object_type='rating_scale',
            number=rating_scale_orig.id)

        # Create a new ReportingTypeInfo record
        reporting_type_info, _ = get_or_create_reporting_type_info(
            reporting_type=reporting_type,
            change_reason=change_reason,
            reporting_reason_text=create_reporting_reason_string(
                reporting_reason),
            hash_string=create_hash_string(unique_identifier_rating_scale,
                                           reporting_type))

        # Create a new record
        rating_scale_esma = RatingScaleESMA.objects.create(
            reporting_type_info=reporting_type_info,
            xml_file=xml_file,

            # Insert all model fields below here
            rating_scale_code=unique_identifier_rating_scale,
            start_date=rating_scale_orig.start_date,
            end_date=rating_scale_orig.end_date,
            description=rating_scale_orig.description,
        )

        for rating_scope_orig in RatingScopeOrig.objects.filter(
                rating_scale=rating_scale_orig).order_by('id').all():

            unique_identifier_rating_scope = format_reference_number(
                object_type='rating_scope',
                number=rating_scope_orig.id)

            # Create a new record
            RatingScopeESMA.objects.create(
                rating_scale=rating_scale_esma,

                # Insert all model fields below here
                rating_scope_code=unique_identifier_rating_scope,
                time_horizon=rating_scope_orig.time_horizon,
                rating_type=rating_scope_orig.rating_type,
                rating_scale_scope=rating_scope_orig.rating_scale_scope,
                relevant_for_cerep_flag=rating_scope_orig.
                relevant_for_cerep_flag,
                start_date=rating_scope_orig.start_date,
                end_date=rating_scope_orig.end_date,
                    )

        for rating_category_orig in RatingCategoryOrig.objects.filter(
            rating_scale=rating_scale_orig
        ).order_by('id').all():

            unique_identifier_rating_category = format_reference_number(
                object_type='rating_category',
                number=rating_category_orig.id)

            # Create a new record
            rating_category_esma = RatingCategoryESMA.objects.create(
                rating_scale=rating_scale_esma,

                # Insert all model fields below here
                rating_category_code=unique_identifier_rating_category,

                value=rating_category_orig.value,
                label=rating_category_orig.label,
                description=rating_category_orig.description,
            )

            for rating_notch_orig in RatingNotchOrig.objects.filter(
                rating_category=rating_category_orig
            ).order_by('id').all():

                unique_identifier_rating_notch = format_reference_number(
                    object_type='rating_notch',
                    number=rating_notch_orig.id)

                # Create a new record
                RatingNotchESMA.objects.create(
                    rating_category=rating_category_esma,

                    # Insert all model fields below here
                    rating_notch_code=unique_identifier_rating_notch,

                    value=rating_notch_orig.value,
                    label=rating_notch_orig.label,
                    description=rating_notch_orig.description,
                )
