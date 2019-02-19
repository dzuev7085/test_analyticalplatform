"""
At the core of a rating and of Nordic Credit Rating's business model is the
issuer. This model defines an issuer, including meta data linked to the
issuer.
"""
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, validate_email
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from tinymce import HTMLField

from a_helper.static_database_table.models.gics import GICSSubIndustry
from datalake.gleif.command import GLEIFEditor
from a_helper.other.sql import SQL

from simple_history.models import HistoricalRecords

ALLOWED_ISSUER_TYPES = (
    (1, 'Corporate'),
    (2, 'Financial institution'),
    (3, 'Real estate corporate')
)


class ProcessQuerySet(models.QuerySet):
    """ProcessQuerySet class."""

    def is_live(self):
        """Return all decisions that have not been deleted."""
        return self.filter(inactivated__isnull=True)

    def list_eligible_for_assessment(self):
        """List all issuers that are eligible for getting a credit
        assessment."""

        sql = '''
        SELECT        i.id
                    , i.legal_name
        FROM          public.issuer_issuer as i
        WHERE         i.issuer_type_id IN (1, 3)
        AND           i.gics_sub_industry_id IS NOT NULL
        AND           i.inactivated IS NULL
        AND           i.id NOT IN (SELECT issuer_id
                                   FROM   public.rating_process_ratingdecision)
        AND           i.id NOT IN (SELECT issuer_id
                                   FROM   public.credit_assessment_assessmentjob)
        ORDER BY      i.legal_name
        '''  # noqa: E501

        return self.raw(sql)

    def list_all(self):
        """Get all companies using an optimized query."""

        sql = '''
        SELECT            i.id
                        , gs.name as sector_name
                        , country.name as country
                        , i.legal_name as legal_name
                        , CASE WHEN it.description = 1 THEN 'Corporate'
                               WHEN it.description = 2 THEN 'Financial'
                               WHEN it.description = 3 THEN 'Real estate'
                          END as issuer_type_name
                        , t9.first_name || ' ' || t9.last_name as p_analyst
                        , t10.first_name || ' ' || t10.last_name as s_analyst
                        , au.first_name || ' ' || au.last_name as c_manager
                        , decision.decided_lt as current_long_term
                        , decision.decided_lt_outlook as current_outlook
                        , CASE WHEN iob.date_time_onboarding_completed IS NULL THEN 'Not Onboarded'
                               WHEN iob.date_time_onboarding_completed IS NOT NULL AND decision_ongoing.id IS NOT NULL THEN 'Rating job in progress'
                               WHEN iob.date_time_onboarding_completed IS NOT NULL AND decision.id IS NOT NULL THEN 'Ongoing surveillance'
                               WHEN iob.date_time_onboarding_completed IS NOT NULL AND decision_ongoing.id IS NULL THEN 'Onboarded'
                          END AS status
                        , CASE WHEN decision_ongoing.process_step = 1 THEN 'Rating job started'
                               WHEN decision_ongoing.process_step = 2 THEN 'Pre-committee'
                               WHEN decision_ongoing.process_step = 3 THEN 'Analytical phase'
                               WHEN decision_ongoing.process_step = 4 THEN 'Post committee'
                               WHEN decision_ongoing.process_step = 5 THEN 'Editing'
                               WHEN decision_ongoing.process_step = 6 THEN 'Issuer confirmation'
                               WHEN decision_ongoing.process_step = 7 THEN 'Analyst final approval'
                               WHEN decision_ongoing.process_step = 8 THEN 'Chair final approval'
                               WHEN decision_ongoing.process_step = 9 THEN 'Ready to be published'
                          END AS status_text
                        , iob.engagement_letter_signed
                        , COALESCE(class.peer_free_text, gsi.name) AS internal_peer

        FROM              issuer_issuer as i
        INNER JOIN        issuer_issuertype as it ON 1 = 1
          AND i.issuer_type_id = it.id
        INNER JOIN        issuer_onboardingprocess as iob ON 1 = 1
          AND iob.issuer_id = i.id
        LEFT OUTER JOIN   auth_user as au ON 1 = 1
          AND i.relationship_manager_id = au.id
        LEFT OUTER JOIN static_database_table_gicssubindustry as gsi
          ON 1 = 1
          AND i.gics_sub_industry_id = gsi.id
        LEFT OUTER JOIN static_database_table_gicsindustry as gi
          ON 1 = 1
          AND gsi.industry_id = gi.id
        LEFT OUTER JOIN static_database_table_gicsindustrygroup as gig
          ON 1 = 1
          AND gi.industry_group_id = gig.id
        LEFT OUTER JOIN static_database_table_gicssector as gs
          ON 1 = 1
          AND gig.sector_id = gs.id
        LEFT OUTER JOIN issuer_analyst as ia
          ON 1 = 1
          AND i.id = ia.issuer_id
        LEFT OUTER JOIN auth_user as t9
          ON 1 = 1
          AND ia.primary_analyst_id = t9.id
        LEFT OUTER JOIN auth_user as t10
          ON 1 = 1
          AND ia.secondary_analyst_id = t10.id
        LEFT OUTER JOIN issuer_address as iadd
          ON 1 = 1
          AND i.id = iadd.issuer_id
        LEFT OUTER JOIN static_database_table_countryregion as country
          ON 1 = 1
          AND iadd.country_id = country.id
        LEFT OUTER JOIN    rating_process_ratingdecision AS decision
          ON 1 = 1
          AND i.id = decision.issuer_id
          AND decision.is_current = True
        LEFT OUTER JOIN    rating_process_ratingdecision AS decision_ongoing
          ON 1 = 1
          AND i.id = decision_ongoing.issuer_id
          AND decision_ongoing.date_time_published IS NULL
          AND decision_ongoing.date_time_deleted IS NULL
        LEFT OUTER JOIN    issuer_classification as class
          ON 1 = 1
          AND i.id = class.issuer_id
        ORDER BY           COALESCE(class.peer_free_text, gsi.name || ': ' || CAST(gsi.code AS TEXT))
                         , i.legal_name
        '''  # noqa: E501

        return self.raw(sql)

    def list_all_rating(self):
        """Get all companies with a rating using an optimized query."""

        sql = '''
        SELECT            i.id
                        , gs.name as sector_name
                        , country.name as country
                        , i.legal_name as legal_name
                        , CASE WHEN it.description = 1 THEN 'Corporate'
                               WHEN it.description = 2 THEN 'Financial'
                               WHEN it.description = 3 THEN 'Real estate'
                          END as issuer_type_name
                        , t9.first_name || ' ' || t9.last_name as p_analyst
                        , t10.first_name || ' ' || t10.last_name as s_analyst
                        , au.first_name || ' ' || au.last_name as c_manager
                        , decision.decided_lt as current_long_term
                        , decision.decided_lt_outlook as current_outlook
                        , CASE WHEN iob.date_time_onboarding_completed IS NULL THEN 'Not Onboarded'
                               WHEN iob.date_time_onboarding_completed IS NOT NULL AND decision_ongoing.id IS NOT NULL THEN 'Rating job in progress'
                               WHEN iob.date_time_onboarding_completed IS NOT NULL AND decision.id IS NOT NULL THEN 'Ongoing surveillance'
                               WHEN iob.date_time_onboarding_completed IS NOT NULL AND decision_ongoing.id IS NULL THEN 'Onboarded'
                          END AS status
                        , CASE WHEN decision_ongoing.process_step = 1 THEN 'Rating job started'
                               WHEN decision_ongoing.process_step = 2 THEN 'Pre-committee'
                               WHEN decision_ongoing.process_step = 3 THEN 'Analytical phase'
                               WHEN decision_ongoing.process_step = 4 THEN 'Post committee'
                               WHEN decision_ongoing.process_step = 5 THEN 'Editing'
                               WHEN decision_ongoing.process_step = 6 THEN 'Issuer confirmation'
                               WHEN decision_ongoing.process_step = 7 THEN 'Analyst final approval'
                               WHEN decision_ongoing.process_step = 8 THEN 'Chair final approval'
                               WHEN decision_ongoing.process_step = 9 THEN 'Ready to be published'
                          END AS status_text
                        , iob.engagement_letter_signed
                        , COALESCE(class.peer_free_text, gsi.name) AS internal_peer
        FROM              issuer_issuer as i
        INNER JOIN        issuer_issuertype as it ON 1 = 1
          AND i.issuer_type_id = it.id
        INNER JOIN        issuer_onboardingprocess as iob ON 1 = 1
          AND iob.issuer_id = i.id
        LEFT OUTER JOIN   auth_user as au ON 1 = 1
          AND i.relationship_manager_id = au.id
        LEFT OUTER JOIN static_database_table_gicssubindustry as gsi
          ON 1 = 1
          AND i.gics_sub_industry_id = gsi.id
        LEFT OUTER JOIN static_database_table_gicsindustry as gi
          ON 1 = 1
          AND gsi.industry_id = gi.id
        LEFT OUTER JOIN static_database_table_gicsindustrygroup as gig
          ON 1 = 1
          AND gi.industry_group_id = gig.id
        LEFT OUTER JOIN static_database_table_gicssector as gs
          ON 1 = 1
          AND gig.sector_id = gs.id
        LEFT OUTER JOIN issuer_analyst as ia
          ON 1 = 1
          AND i.id = ia.issuer_id
        LEFT OUTER JOIN auth_user as t9
          ON 1 = 1
          AND ia.primary_analyst_id = t9.id
        LEFT OUTER JOIN auth_user as t10
          ON 1 = 1
          AND ia.secondary_analyst_id = t10.id
        LEFT OUTER JOIN issuer_address as iadd
          ON 1 = 1
          AND i.id = iadd.issuer_id
        LEFT OUTER JOIN static_database_table_countryregion as country
          ON 1 = 1
          AND iadd.country_id = country.id
        LEFT OUTER JOIN    rating_process_ratingdecision AS decision
          ON 1 = 1
          AND i.id = decision.issuer_id
          AND decision.is_current = True
        LEFT OUTER JOIN    rating_process_ratingdecision AS decision_ongoing
          ON 1 = 1
          AND i.id = decision_ongoing.issuer_id
          AND decision_ongoing.date_time_published IS NULL
          AND decision_ongoing.date_time_deleted IS NULL
        LEFT OUTER JOIN    issuer_classification as class
          ON 1 = 1
          AND i.id = class.issuer_id
        WHERE decision.is_current = True
        ORDER BY           COALESCE(class.peer_free_text, gsi.name || ': ' || CAST(gsi.code AS TEXT))
                         , i.legal_name
        '''  # noqa: E501

        return self.raw(sql)

    def list_all_assessment(self, issuer_id_list):
        """Get all companies with an assessment."""

        sql = '''
        WITH t1 AS (
        SELECT     i.id
                 , i.legal_name
                 , i.issuer_type_id
                 , cr.iso_31661_alpha_2 as ccy
                 , COALESCE(class.peer_free_text, gsi.name) as sort_key
        FROM       issuer_issuer AS i
        LEFT OUTER JOIN issuer_address AS ia
          ON 1 = 1
          AND ia.issuer_id = i.id
        LEFT OUTER JOIN static_database_table_countryregion AS cr
          ON 1 = 1
          AND cr.id = ia.country_id
        LEFT OUTER JOIN    static_database_table_gicssubindustry as gsi
          ON 1 = 1
          AND i.gics_sub_industry_id = gsi.id
        LEFT OUTER JOIN    issuer_classification AS class
          ON 1 = 1
          AND i.id = class.issuer_id
        WHERE i.issuer_type_id IN %s
        ORDER BY sort_key, i.legal_name
        )
        SELECT           i.id
                       , i.legal_name AS i_name
                       , i.ccy
                       , i.sort_key AS internal_peer
                       , i.issuer_type_id as i_id
                       , COALESCE(dec_current.date_time_published, ass_current.date_time_approval) AS current_date_time_approval
                       , ass_current.id AS current_id

                       , ass_progress.id AS progress_id
                       , ass_progress.process_step AS progress_process_step
                       , ass_progress.initiated_by_id AS progress_initiated_by_id
                       , ass_progress.assessment_lt AS progress_assessment_lt

                       , dec_current.id as rating_id

                       , COALESCE(dec_current.initiated_by_id, ass_progress.initiated_by_id, ass_current.initiated_by_id) initiated_by
        FROM             t1 as i
        LEFT JOIN        credit_assessment_assessmentjob AS ass_current ON 1 = 1
          AND ass_current.issuer_id = i.id
          AND ass_current.is_current = True
        LEFT JOIN        credit_assessment_assessmentjob AS ass_progress ON 1 = 1
          AND ass_progress.issuer_id = i.id
          AND ass_progress.is_current = False
          AND ass_progress.date_time_approval IS NULL
        LEFT JOIN         rating_process_ratingdecision as dec_current ON 1 = 1
          AND dec_current.issuer_id = i.id
          AND dec_current.is_current = True
        WHERE 1 = 1
          AND     (( ass_current.id IS NOT NULL
                     OR  ass_progress.id IS NOT NULL ) OR dec_current.id IS NOT NULL )
        ORDER BY internal_peer
               , legal_name
          '''  # noqa: E501

        return self.raw(sql, [tuple(issuer_id_list)])

    def list_onboarded(self):
        """List issuers that are onboarded."""

        return self.filter(
            onboarding_issuer_link__date_time_onboarding_completed__isnull=False)  # noqa: E501


class ProcessManager(models.Manager):
    """Process manager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    def is_live(self):
        """Get all companies that are live (not deleted)."""
        return self.get_queryset().is_live()

    def list_all(self):
        """Get all companies using an optimized query."""
        return self.get_queryset().list_all()

    def list_all_rating(self):
        """Get all companies with a rating using an optimized query."""
        return self.get_queryset().list_all_rating()

    def list_eligible_for_assessment(self):
        """List all issuers that are eligible for getting a credit
        assessment."""

        return self.get_queryset().list_eligible_for_assessment()

    def list_all_assessment(self, issuer_id_list):
        """Get all companies with an assessment."""

        return self.get_queryset().list_all_assessment(issuer_id_list)

    def list_onboarded(self):
        """List issuers that are onboarded."""
        return self.get_queryset().list_onboarded()


class IssuerType(models.Model):
    """
    Current, Nordic Credit Rating's business model revolvers around three
    type of issuers: corporates, corporates in the real estate sector and
    financials.

    The ID# linked to each issuer type is used throughout the web site, in
    views as well as in templates. The order and numbering may thus not be
    changed.
    """
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    description = models.IntegerField(
        choices=ALLOWED_ISSUER_TYPES,
        unique=True)

    def __str__(self):
        return '{}'.format(self.get_description_display())


# Create your models here.
class Issuer(models.Model):
    """Define an issuer. The issuer is the core object
    of the analytical toolkit."""

    # Add version history to the model
    history = HistoricalRecords()

    objects = ProcessManager()

    def __str__(self):
        """Return a human readable representation of each record."""
        return '{}'.format(self.legal_name)

    class Meta:
        """Meta class."""
        ordering = ['legal_name']

    @property
    def internal_identifier(self):
        """Internal identifier for model.
        Same as in template_tags."""

        return 'I' + str(self.pk).zfill(6)

    @property
    def peer_sector(self):
        """Return the NCR defined peer group."""

        return self.gics_sub_industry

    @property
    def is_onboarded(self):
        """Flag if the issuer has been onboarded."""

        if self in Issuer.objects.list_onboarded():
            return True
        else:
            return False

    parent_company = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # The system wide unique identifier for an issuer
    # https://www.leiroc.org/lei.htm
    lei = models.CharField(
        max_length=20,
        unique=True
    )

    # A name in the model for the issuer's legal name
    # Is populated from GLEIF repository upon insertion
    # of issuer
    short_name = models.CharField(
        db_index=True,
        max_length=128,
        null=True,
        blank=True,
    )

    legal_name = models.CharField(
        db_index=True,
        max_length=128,
        unique=True
    )

    # Provide a description of the issuer. This description
    # is for internal as well as external use.
    description = HTMLField(
        null=True,
        blank=True,
    )

    # The person in the Commercial team responsible for
    # managing the relationship with the issuer
    relationship_manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="relationship_manager_link",
        null=True,
        blank=True
    )

    # Type of issuer. Determines which methodology is
    # used
    issuer_type = models.ForeignKey(
        IssuerType,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    # Defines what sector the issuer belongs to
    # This is based on the Global Industry Classification Standard (GICS)
    gics_sub_industry = models.ForeignKey(
        GICSSubIndustry,
        on_delete=models.PROTECT,
        related_name="issuer_gicssubindustry_link",
        null=True,
        blank=True
    )

    # This is if we want to de-activate the entity for some reason
    # Allows us to remove the issuer without physically delete it from the
    # database tables
    inactivated = models.DateTimeField(
        null=True,
        blank=True
    )


class Analyst(models.Model):
    """Define a primary and, if applicable,
    secondary analyst for the issuer."""

    # Add version history to the model
    history = HistoricalRecords()

    def __str__(self):
        """Return a human readable representation of each record."""
        return 'Analysts for {}'.format(self.issuer.legal_name)

    issuer = models.OneToOneField(
        Issuer,
        on_delete=models.PROTECT
    )

    primary_analyst = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="primary_analyst_link",
        null=True,
        blank=True
    )

    secondary_analyst = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="secondary_analyst_link",
        null=True,
        blank=True
    )


CONTACT_TYPES = (
    (1, 'Primary contact'),
    (2, 'Secondary contact'),
)


class InsiderList(models.Model):
    """InsiderList class."""

    # Add version history to the model
    history = HistoricalRecords()

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s %s is on insider list for %s %s' % (
            self.first_name,
            self.last_name,
            self.issuer.legal_name,
            'as ' + self.get_contact_type_display().lower()
            if self.get_contact_type_display() else ''
        )

    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
        related_name="insider_list_issuer_link",
    )

    company = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="If other company than issuer."
    )

    contact_type = models.IntegerField(
        db_index=True,
        choices=CONTACT_TYPES,
        null=True,
        blank=True,
        help_text="Leave as '----' if not primary or secondary contact."
    )

    first_name = models.CharField(
        db_index=True,
        max_length=100,
        blank=False
    )

    last_name = models.CharField(
        db_index=True,
        max_length=100,
        blank=False
    )

    email = models.CharField(
        max_length=100,
        blank=False,
        validators=[validate_email],
        help_text="Eg name@host.com"
    )

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be "
                                         "entered in the format: "
                                         "'+999999999999'. "
                                         "Up to 15 digits allowed.")
    # validators should be a list
    phone_number = models.CharField(validators=[phone_regex],
                                    max_length=17,
                                    help_text="Eg +nnnnnnnnnn")

    role = models.CharField(
        db_index=True,
        max_length=100,
        blank=False,
        help_text="Eg 'Debt analyst' or 'Legal counsel'"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
    )

    date_deletion = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )


class OnboardingProcess(models.Model):
    """Onboarding process for Issuer."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return 'Onboarding for %s' % (
            self.issuer.legal_name,
        )

    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
        related_name="onboarding_issuer_link",
    )

    engagement_letter_signed = models.BooleanField(
        default=False
    )

    date_time_engagement_letter_signed = models.DateTimeField(
        blank=True,
        null=True,
    )

    issuer_long_term = models.BooleanField(
        default=False
    )

    issuer_short_term = models.BooleanField(
        default=False
    )

    instrument_rating = models.BooleanField(
        default=False,
    )

    target_delivery_date = models.DateField(
        blank=True,
        null=True,
    )

    date_time_onboarding_completed = models.DateTimeField(
        blank=True,
        null=True,
    )


class EventType(models.Model):
    """EventType model."""

    def __str__(self):
        return self.description

    description = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )


class Event(models.Model):
    """Log event that occur on the issuer level.."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s: "%s" on %s' % (
            self.issuer.legal_name,
            self.event_type,
            self.timestamp.strftime("%Y-%m-%d")
        )

    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
        related_name="process_issuer_link",
    )

    triggered_by_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="event_user_link",
        null=False,
        blank=False
    )

    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    timestamp = models.DateTimeField(
        db_index=True,
        default=timezone.now
    )


@receiver(post_save, sender=Issuer)
def create_issuer(sender, instance, created, **kwargs):
    """
    Whenever an issuer_corporate is added to the system,
    we also want a record in the table for
    Analysts
    """
    if created:
        Analyst.objects.create(issuer=instance)

        OnboardingProcess.objects.create(
            issuer=instance)

        # create database connection and session
        db_connection = SQL('datalake')

        # Get data from GLEIF database
        # If LEI does not exist, it will start with LEI_
        if not instance.lei[0:4] == 'LEI_':
            GLEIFEditor(db_connection).upsert(instance.lei)


@receiver(post_save, sender=Issuer)
def save_issuer(sender, instance, created, **kwargs):
    """
    Post save signal to check if all requirements to move to the next step in
    the onboarding process have been fulfilled.

    This signal does the test if the Issuer-model has been updated.

    If they have been fulfilled, set the 'Analyst appointed'-step in the
    OnboardingProcess-model to True.
    """
    issuer = Issuer.objects.get(id=instance.id)
    analysts = Analyst.objects.get(issuer=issuer)

    if issuer.issuer_type and analysts.primary_analyst:
        onboarding_obj = OnboardingProcess.objects.get(issuer=issuer)
        onboarding_obj.analysts_appointed = True
        onboarding_obj.save()


@receiver(post_save, sender=Analyst)
def save_analyst(sender, instance, created, **kwargs):
    """
    Post save signal to check if all requirements to move to the next step in
    the onboarding process have been fulfilled.

    This signal does the test if the Analyst-model has been updated.

    If they have been fulfilled, set the 'Analyst appointed'-step in the
    OnboardingProcess-model to True.
    """
    issuer = Issuer.objects.get(id=instance.issuer_id)
    analysts = Analyst.objects.get(issuer=issuer)

    if issuer.issuer_type and analysts.primary_analyst:
        onboarding_obj = OnboardingProcess.objects.get(issuer=issuer)
        onboarding_obj.analysts_appointed = True
        onboarding_obj.save()
