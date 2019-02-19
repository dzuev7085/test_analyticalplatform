"""Store data for changes in ratings for issuers or issues."""
from django.db import models

from integrations.esma.models.xml_file import XMLFile

from rating_process.models.rating_decision import RatingDecision
from gui.templatetags.template_tags import format_reference_number
from upload.models import AnalyticalDocument
from rating_process.models.press_release import PressRelease

from a_helper.static_database_table.models.rating_scale import RatingScale
from a_helper.static_database_table.models.country import CountryRegion
from a_helper.static_database_table.models.currency import Currency

from issue.models import Issue


class ProcessQuerySet(models.QuerySet):
    """Process filters."""

    def last_valid_record(self):
        """Get last successful record sent to ESMA."""
        return self.filter(xml_file__status_code=1).order_by('-id')


class ProcessManager(models.Manager):
    """Process manager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    def last_valid_record(self):
        """Get all records that should be sent to ESMA"""
        return self.get_queryset().last_valid_record()


class QTRatingCreateData(models.Model):
    """RatingCreateData model."""

    # Important for the script that sends data to ESMA.
    ordering = ['-id']

    objects = ProcessManager()

    def __str__(self):
        """Represent the class."""
        return '{} | {}'.format(
            self.rating_decision,
            self.xml_file)

    xml_file = models.OneToOneField(
        XMLFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    insertion_date = models.DateField(
        auto_now_add=True,
    )

    reporting_type = models.IntegerField(
        choices=((1, 'NEW'),),
        null=False,
        blank=False,
    )

    rating_identifier = models.IntegerField(
        blank=False,
        null=False,
    )

    @property
    def rating_identifier_formatted(self):
        """An identifier that follows the rating through its
        live span."""

        # Preliminary ratings have their own ID's
        if self.rating_decision.is_preliminary:
            b = 'P_'
        else:
            b = ''

        b += (format_reference_number(
            number=self.rating_identifier,
            object_type='rating_decision') + '_' +
             self.qtratingaction.qtratinginfo.
             get_time_horizon_display())

        try:
            # This is an issue rating, add issuer suffic
            if self.qtratingaction.qtratinginfo.qtinstrumentinfo.\
                    instrument_internal_code:

                    b += '_' + self.qtratingaction.qtratinginfo.\
                        qtinstrumentinfo.instrument_internal_code
        except:  # noqa: E722
            #  todo: catch RelatedObjectDoesNotExist
            pass

        return b

    @property
    def rating_action_identifier(self):
        """A unique identifier for this record?."""
        return format_reference_number(number=self.pk,
                                       object_type='rating_action')

    # RatingActionInfo links back here
    # RatingAction links back here

    hash = models.CharField(
        db_index=True,
        max_length=32,
        blank=True,
        null=True,
    )


class QTRatingActionInfo(models.Model):
    """RatingActionInfo model."""

    def __str__(self):
        return '{} | {} | {}'.format(
            self.rating_create_data,
            self.get_rating_issuance_location_display(),
            self.get_rating_solicited_unsolicited_display(),
        )

    rating_create_data = models.OneToOneField(
        QTRatingCreateData,
        on_delete=models.PROTECT,
    )

    """
    I - Issued in the Union
    E - Endorsed
    T - Issued in a third CountryRegion by a certified CRA
    O - Other (not-endorsed)
    N - Not available (only valid before 01/01/2011)
    """
    rating_issuance_location = models.IntegerField(
        choices=((1, 'I'),
                 (2, 'E'),
                 (3, 'T'),
                 (4, 'O'),
                 (5, 'N'),),
        null=False,
        blank=False,
    )

    # ActionDateInfo links back to here
    # LeadAnalystInfo links back to here

    """
    S - if the rating is solicited,
    U - if the rating is unsolicited without participation
    P - if the rating is unsolicited with participation
    N – in case of not endorsed ratings if the rating is
        unsolicited and the participation is unspecified.
    """
    rating_solicited_unsolicited = models.IntegerField(
        choices=((1, 'S'),
                 (2, 'U'),
                 (3, 'P'),
                 (4, 'N'),),
        null=False,
        blank=False,
    )

    press_release_flag = models.BooleanField(
        default=False,
    )

    press_release = models.ForeignKey(
        PressRelease,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    research_report_flag = models.BooleanField(
        default=False,
    )

    research_report = models.ForeignKey(
        AnalyticalDocument,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )


class QTActionDateInfo(models.Model):
    """ActionDateInfo model."""

    def __str__(self):
        return '{} | {}'.format(
            self.rating_action_info,
            self.communication_date,
        )

    rating_action_info = models.OneToOneField(
        QTRatingActionInfo,
        on_delete=models.PROTECT,
    )

    validity_date = models.DateTimeField(
        null=False,
        blank=False,
    )

    communication_date = models.DateTimeField(
        null=False,
        blank=False,
    )

    decision_date = models.DateTimeField(
        null=False,
        blank=False,
    )


class QTLeadAnalystInfo(models.Model):
    """LeadAnalystInfo model."""

    def __str__(self):
        return '{} | {}'.format(
            self.rating_action_info,
            self.lead_analyst_code,
        )

    rating_action_info = models.OneToOneField(
        QTRatingActionInfo,
        on_delete=models.PROTECT,
    )

    country_model = models.ForeignKey(
        CountryRegion,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    lead_analyst_code = models.CharField(
        max_length=40,
        blank=False,
        null=False,
    )

    @property
    def lead_analyst_country_code(self):
        """Return "ISO 3166-1 Alpha-2 code."""
        return self.country_model.iso_31661_alpha_2


class QTRatingAction(models.Model):
    """RatingAction model."""

    def __str__(self):
        return '{} | {}'.format(
            self.rating_create_data,
            self.get_action_type_display(),
        )

    rating_create_data = models.OneToOneField(
        QTRatingCreateData,
        on_delete=models.PROTECT,
    )

    """
    OR – in case of outstanding rating (only for first time reporting)
    PR - in case of preliminary rating
    NW - in case the rating is issued for the first time
    UP - in case the rating is upgraded
    DG - in case the rating is downgraded
    AF - in case the rating is affirmed
    DF - in case a rated issuer or instrument is assigned to or removed
         from a default status and the default is not linked with another
         rating action
    SP - in case the rating is suspended
    WD - in case the rating is withdrawn
    OT - in case the rating is placed to or removed from the
         outlook/trend status
    WR - in case the rating is placed to or removed from the
         watch/review status
    """
    action_type = models.IntegerField(
        blank=False,
        null=False,
        choices=((1, 'OR'),
                 (2, 'PR'),
                 (3, 'NW'),
                 (4, 'UP'),
                 (5, 'DG'),
                 (6, 'AF'),
                 (7, 'DF'),
                 (8, 'SP'),
                 (9, 'WD'),
                 (10, 'OT'),
                 (11, 'WR'),),
    )

    # RatingValue links back here

    # RatingInfo links back here

    """
    An outlook/Watch/Suspension/Default status is assigned,
    kept or removed by the CRA according to its relevant
    policy.
    P - status is placed
    M - status is maintained
    R - status is removed
    """
    # TODO: how does this work?
    owsd_status = models.IntegerField(
        blank=True,
        null=True,
        choices=((1, 'P'),
                 (2, 'M'),
                 (3, 'R'),),
    )

    """
    Identifies the outlook/trend assigned or removed to a
    rating by the CRA according to its relevant policy.
    POS - in case of a positive outlook
    NEG - in case of a negative outlook
    EVO - in case of an evolving  or developing outlook
    STA - in case of a stable outlook
    """
    outlook_trend = models.IntegerField(
        blank=True,
        null=True,
        choices=((1, 'POS'),
                 (2, 'NEG'),
                 (3, 'EVO'),
                 (4, 'STA'),),
    )

    """
    Identifies the watch/review status assigned to or
    removed from a rating by the CRA according to its
    relevant policy.
    POW - in case of a positive watch/review
    NEW - in case of a negative watch/review
    EVW - in case of an evolving or developing watch/review
    UNW - in case of a watch/review with uncertain direction
    """
    watch_review = models.IntegerField(
        blank=True,
        null=True,
        choices=((1, 'POW'),
                 (2, 'NEW'),
                 (3, 'EVW'),
                 (4, 'UNW'),),
    )

    """
    Identifies the reason of a withdrawal action.
    1 - in case of incorrect or insufficient information on issuer/issue
    2 - in case of bankruptcy of the rated entity or debt restructuring
    3 - in case of reorganization of rated entity (including the merger
        or acquisition of the rated entity)
    4 - in case of the end of maturity of the debt obligation, or in case
        the debt is redeemed, called, prefunded, cancelled
    5 - in case of automatic invalidity of rating due to business model
        of CRA (such as expiry of ratings valid for a predetermined period)
    6 – in case of rating withdrawal due to other reasons
    7 - in case the rating relates to 10% shareholder on an impacted
        entity (as set out in Annex I, Section B, Point 3 of the Regulation)
    8 – in case of client’s request
    """
    withdrawal_reason_type = models.IntegerField(
        blank=True,
        null=True,
        choices=((1, 1),
                 (2, 2),
                 (3, 3),
                 (4, 4),
                 (5, 5),
                 (6, 6),
                 (7, 7),
                 (8, 8),),
    )


class QTRatingValue(models.Model):
    """RatingValue model."""

    def __str__(self):
        return '{} | {} | {} | Default: {}'.format(
            self.rating_action,
            self.rating_scale,
            self.rating_value,
            self.default_flag,
        )

    rating_action = models.OneToOneField(
        QTRatingAction,
        on_delete=models.PROTECT,
    )

    rating_scale = models.ForeignKey(
        RatingScale,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    rating_value = models.IntegerField(
        blank=False,
        null=False,
    )

    @property
    def rating_scale_code(self):
        """A code used internally by ESMA"""
        return format_reference_number(number=self.rating_scale.pk,
                                       object_type='rating_scale')

    default_flag = models.BooleanField(
        default=False,
    )


class QTRatingInfo(models.Model):
    """RatingInfo model."""

    def __str__(self):
        return '{} | {} | {} | {}'.format(
            self.rating_action,
            self.get_rating_type_display(),
            self.get_rated_object_display(),
            self.get_type_of_rating_for_erp_display(),
        )

    rating_action = models.OneToOneField(
        QTRatingAction,
        on_delete=models.PROTECT,
    )

    country_model = models.ForeignKey(
        CountryRegion,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    responsible_cra_lei = models.CharField(
        max_length=20,
        null=False,
        blank=False,
    )

    issuer_cra_lei = models.CharField(
        max_length=20,
        null=False,
        blank=False,
    )

    """
    C - corporate ratings
    S - Sovereign and public finance ratings
    T - Structured finance ratings
    O – Other financial instruments
    """
    rating_type = models.IntegerField(
        choices=((1, 'C'),
                 (2, 'S'),
                 (3, 'T'),
                 (4, 'O'),),
        null=False,
        blank=False,
    )

    other_rating_type = models.TextField(
        max_length=300,
        null=True,
        blank=True,
    )

    """
    ISR = issuer
    INT = instrument
    """
    rated_object = models.IntegerField(
        choices=((1, 'ISR'),
                 (2, 'INT'),),
        null=False,
        blank=False,
    )

    """
    L - applicable to long term ratings
    S – applicable to short term ratings
    """
    time_horizon = models.IntegerField(
        choices=((1, 'L'),
                 (2, 'S'),),
        null=False,
        blank=False,
    )

    @property
    def country(self):
        """Return "ISO 3166-1 Alpha-2 code."""
        return self.country_model.iso_31661_alpha_2

    local_foreign_currency = models.IntegerField(
        choices=((1, 'LC'),
                 (2, 'FC'),),
        null=False,
        blank=False,
        default=2,
    )

    # IssuerInfo links back here
    # InstrumentInfo links back here

    issuer_rating_type_code = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )

    debt_classification_code = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )

    """
    FI - for financial institution rating including banks, brokers and
         dealers,
    IN - for insurance institution rating
    CO - for corporate institution rating that are not included in
         'FI' or 'IN'
    """
    industry = models.IntegerField(
        choices=((1, 'FI'),
                 (2, 'IN'),
                 (3, 'CO'),),
        null=False,
        blank=False,
    )

    """
    SV – for State rating
    SM – for regional or local-authority rating
    IF – for international financial institution rating
    SO – for supranational organizations rating other than 'IF'
    PE – for public entities rating
    """
    sector = models.IntegerField(
        choices=((1, 'FI'),
                 (2, 'IN'),
                 (3, 'CO'),),
        null=True,
        blank=True,
    )

    """
    ABS -  for ABS rating
    RMBS -  for RMBS rating
    CMBS -  for CMBS rating
    CDO -  for CDO rating
    ABCP -  for ABCP rating
    OTH -  for Other
    """
    asset_class = models.IntegerField(
        choices=((1, 'ABS'),
                 (2, 'RMBS'),
                 (3, 'CMBS'),
                 (4, 'CDO'),
                 (5, 'ABCP'),
                 (6, 'OTH)'),),
        null=True,
        blank=True,
    )

    """
    CCS - If ABS: Credit card receivable backed securities
    ALB - If ABS: Auto loan backed securities
    CNS - If ABS: Consumer loan backed security
    SME - If ABS: Small and medium sized enterprises loan backed securities
    LES - If ABS: Leases to individual or business backed security
    HEL - If RMBS: Home equity loans
    PRR - If RMBS: Prime RMBS,
    NPR - If RMBS: Non-prime RMBS
    CFH - If CDO: Cash flow and hybrid CDOs/CLOs
    SDO - If CDO: Synthetic CDOs/CLOs
    MVO - If CDO: Market value CDOs
    SIV - If OTH: structured investment vehicles
    ILS - If OTH: insurance-linked securities
    DPC - If OTH: derivative product companies
    SCB - If OTH: structured covered bonds
    OTH – Other.
    """
    sub_asset = models.IntegerField(
        choices=((1, 'CCS'),
                 (2, 'ALB'),
                 (3, 'CNS'),
                 (4, 'SME'),
                 (5, 'LES'),
                 (6, 'HEL'),
                 (7, 'PRR'),
                 (8, 'NPR'),
                 (9, 'CFH'),
                 (10, 'SDO'),
                 (11, 'MVO'),
                 (12, 'SIV'),
                 (13, 'ILS'),
                 (14, 'DPC'),
                 (15, 'SCB'),
                 (16, 'OTH'),),
        null=True,
        blank=True,
    )

    other_sub_asset = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )

    """
    NXI - the rating is not exclusively produced for and disclosed to
          investors for a fee
    EXI - the rating is exclusively produced for and disclosed to
          investors for a fee
    """
    type_of_rating_for_erp = models.IntegerField(
        choices=((1, 'NXI'),
                 (2, 'EXI'),),
        null=False,
        blank=False,
        default=2,  # to ensure we don't accidentally report anything
    )

    relevant_for_cerep = models.BooleanField(
        default=False,
    )

    # PrecedingPreliminaryRating links back here


class QTIssuerInfo(models.Model):
    """IssuerInfo ."""

    def __str__(self):
        return '{} | {}'.format(
            self.rating_info,
            self.issuer_name,
        )

    rating_info = models.OneToOneField(
        QTRatingInfo,
        on_delete=models.PROTECT,
    )

    lei_code = models.CharField(
        max_length=20,
        blank=False,
        null=False,
    )

    @property
    def issuer_internal_code(self):
        """A unique identifier for this record?."""
        return format_reference_number(
            number=self.rating_info.rating_action.rating_create_data.
            rating_decision.issuer.pk,
            object_type='issuer')

    issuer_name = models.CharField(
        max_length=90,
        blank=False,
        null=False,
    )


class QTPrecedingPreliminaryRating(models.Model):
    """PrecedingPreliminaryRating model."""

    def __str__(self):
        return '{} | {}'.format(
            self.rating_info,
            self.preceding_preliminary_rating_flag,
        )

    rating_info = models.OneToOneField(
        QTRatingInfo,
        on_delete=models.PROTECT
    )

    preceding_preliminary_rating_flag = models.BooleanField()

    @property
    def preliminary_rating_identifier(self):
        """ESMA-specified unique identifier for preliminary rating.

        If instrument is true, return instrument identifier,
        else rating identifier."""

        if self.preceding_preliminary_rating_flag:
            b = 'P_'

            b += format_reference_number(
                number=self.rating_info.rating_action.
                rating_create_data.rating_decision.
                esma_rating_identifier,
                object_type='rating_decision',
            )

            b += self.rating_info.rating_action.\
                qtratinginfo.get_time_horizon_display()

            try:
                b += self.rating_info.qtinstrumentinfo.instrument_internal_code
            except:  # noqa: E722
                pass

            return b


class QTInstrumentInfo(models.Model):
    """Instrument info class.

    As soon as the information on ISIN
    (and any of the other instrument characteristics)
    is available, you need to submit it to RADAR.
    """

    def __str__(self):
        return '{}'.format(
            self.isin_code,
        )

    rating_info = models.OneToOneField(
        QTRatingInfo,
        on_delete=models.PROTECT,
    )

    issue = models.ForeignKey(
        Issue,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    isin_code = models.CharField(
        max_length=12,
        blank=True,
        null=True,
    )

    @property
    def instrument_internal_code(self):
        """Internal ID for the issue."""
        return format_reference_number(
            number=self.issue.pk,
            object_type='issue')

    instrument_unique_identifier = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )

    issuance_date = models.DateField(
        blank=True,
        null=True,
    )

    maturity_date = models.DateField(
        blank=True,
        null=True,
    )

    outstanding_issue_volume = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        blank=True,
        null=True
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    @property
    def issue_volume_currency_code(self):
        """The ISO 4217 currency code."""

        return self.currency.currency_code_alpha_3

    program_deal_issuance_name = models.CharField(
        max_length=140,
        blank=True,
        null=True,
    )

    """
    BND - bonds
    CBR - covered bonds that fall under the requirements
          referred to in Article 129 of Regulation (EU) No
          575/2013 and Article 52(4) of Directive 2009/65/EC
    OCB - other types of covered bonds, for which the credit
          rating agency has used specific covered bonds methodologies,
          models or key rating assumptions for issuing the credit
          rating and does not fall under the requirements of point (b)
    OTH - other types of corporate issues that cannot be classified
          in one of the preceding types
    """
    corporate_issue_classification = models.IntegerField(
        choices=((1, 'BND'),
                 (2, 'CBR'),
                 (3, 'OCB'),
                 (4, 'OTH'),),
        default=1,
        null=False,
        blank=False,
    )

    other_corporate_issues = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    issue_program_code = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )

    tranche_class = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )

    serie_program_code = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )

    """
    Complexity indicator: It specifies the
    complexity grade assigned to the ratings
    considering the number of originators,
    counter parties, countries, the need to
    develop, complex colateral, etc.
    """
    complexity_indicator = models.IntegerField(
        choices=((1, 'S'),
                 (2, 'C'),),
        blank=True,
        null=True,
    )

    """
    Structured Finance Transaction type: Indicates
    whether the instrument refers to a Stand-alone or master-Trust
    """
    structured_finance_transaction_type = models.IntegerField(
        choices=((1, 'S'),
                 (2, 'M'),),
        blank=True,
        null=True,
    )


class QTOriginator(models.Model):
    """QTOriginator info class.

    Originator information: Informations on the issuer
    including internal id, LEI code, name
    """

    def __str__(self):
        return '{}'.format(
            self.originator_name,
        )

    instrument_info = models.ForeignKey(
        'QTInstrumentInfo',
        on_delete=models.PROTECT,
    )

    bic_code = models.CharField(
        max_length=11,
        blank=True,
        null=True,
    )

    internal_code = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )

    lei = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    originator_name = models.CharField(
        max_length=90,
        blank=True,
        null=True,
    )
