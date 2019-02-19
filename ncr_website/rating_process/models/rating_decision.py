from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from pycreditrating import (
    RATING_LONG_TERM_OUTLOOK_REVERSE_TUPLE,
    RATING_LONG_TERM_REVERSE_TUPLE,
    RATING_SHORT_TERM_TUPLE
)
from simple_history.models import HistoricalRecords
from tinymce.models import HTMLField

from integrations.esma.const import LOOKBACK
from issuer.models import Issuer
from rating_process.const import PROCESS_STEPS

today = timezone.datetime.today()


class BaseModel(models.Model):
    """BaseModel class."""

    class Meta:
        """Mega class."""
        abstract = True  # specify this model as an Abstract Model
        app_label = 'rating_process'


class EventType(BaseModel):
    """List the various RatingActionTypes.
    Populated through fixtures."""

    def __str__(self):
        return self.description

    description = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )


class RatingType(BaseModel):
    """List the various rating types.
    Populated through fixtures."""

    def __str__(self):
        return self.description

    description = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )


class ProcessQuerySet(models.QuerySet):
    """Process filters."""

    def base_filter(self):
        """Return all decisions that have not been deleted."""
        return self.filter(date_time_deleted__isnull=True)

    # Current ratings
    def valid_decisions(self):
        """Return all published ratings."""
        return self.filter(date_time_published__isnull=False,
                           date_time_deleted__isnull=True).order_by(
                               '-date_time_committee',
                               '-date_time_published')

    def public_ratings(self):
        """Return ratings that are in the public domain."""

        return self.filter(rating_type__pk=1)

    def esma(self):
        """Return rating decisions that are to be reported to ESMA."""

        # At the moment, only send public ratings
        return self.valid_decisions().filter(
            rating_type__id__in=[1],
            date_time_published__gte=timezone.now() - timedelta(
                days=LOOKBACK,)).order_by('date_time_published')

    def published_today(self):
        """Return ratings that were published today."""
        return self.filter(date_time_published__year=today.year,
                           date_time_published__month=today.month,
                           date_time_published__day=today.day)

    # Toll gates
    def has_confirmed_chair(self):
        """Return all records where chair is confirmed."""
        return self.filter(chair__isnull=False,
                           chair_confirmed=True)

    def has_confirmed_date(self):
        """Return all records where date is confirmed."""
        return self.filter(date_time_committee__isnull=False,
                           date_time_committee_confirmed=True)

    def has_passed_committee_date(self):
        """Return all records where date and time for
        rating committee has been passed."""
        return self.filter(date_time_committee__lt=timezone.now())

    # Error management
    def missing_chair(self):
        """Return all records where a chair has not been recommended."""
        return self.filter(chair__isnull=True)

    def chair_not_confirmed(self):
        """Return all records where the chair has been
        suggested but not confirmed."""
        return self.filter(chair__isnull=False,
                           chair_confirmed=False)

    def missing_date_time_committee(self):
        """Return all records where a date has not been proposed."""
        return self.filter(date_time_committee__isnull=True)

    def date_time_committee_not_confirmed(self):
        """Return all records where a date has
        been proposed but not confirmed."""
        return self.filter(date_time_committee__isnull=False,
                           date_time_committee_confirmed=False)

    # Misc
    def confirmed_non_chair_members(self):
        """How many committee members have confirmed their membership?"""
        return self.filter(ratingjob__member_confirmed=True)

    ##############################################
    # Below here is some stuff for the new version
    def in_progress(self):
        """A rating is in progress if it is not published."""
        return self.filter(date_time_deleted__isnull=True,
                           date_time_published__isnull=True)

    def in_committee(self):
        """All ratings that are submitted for the committee."""

        return self.filter(
            process_step=4,
            date_time_committee__gte=timezone.now() - timedelta(
                hours=2, ))

    def pre_committee_questions_answered(self):
        """Is pre committee process step passed?"""
        return self.filter(controlquestion__question__stage=2,
                           controlquestion__answer_correct=False)

    def analyst_final_approval_questions_answered(self):
        """Have all questions been correctly answered?"""
        return self.filter(controlquestion__question__stage=3,
                           controlquestion__answer_correct=False)

    def chair_final_approval_questions_answered(self):
        """Have all questions been correctly answered?"""
        return self.filter(controlquestion__question__stage=4,
                           controlquestion__answer_correct=False)

    def publishing_questions_answered(self):
        """Have all questions been correctly answered?"""
        return self.filter(controlquestion__question__stage=5,
                           controlquestion__answer_correct=False)

    def external_analysis(self):
        """Has an external analytical document been uploaded?"""
        return self.filter(analyticaldocument__document_type__id=10)

    def external_public_analysis(self):
        """Has an external public analytical document been uploaded?"""
        return self.filter(analyticaldocument__document_type__id=15)

    def internal_analysis(self):
        """Has an internal analytical document been uploaded?"""
        return self.filter(analyticaldocument__document_type__id=11)

    def has_editor(self):
        """Is an editor added."""
        return self.filter(jobmember__group__id=2)

    def has_contact_person(self):
        """At least one contact person with issuer"""
        return self.filter(ratingdecisioninsiderlink__gte=1)


class ProcessManager(models.Manager):
    """ProcessManager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    # Process filters
    def base_filter(self):
        """Return all decisions that have not been deleted."""
        return self.get_queryset().base_filter()

    def public_ratings(self):
        """Return ratings that are in the public domain."""
        return self.get_queryset().base_filter().valid_decisions().\
            public_ratings()

    def esma(self):
        """Return rating decisions that are to be reported to ESMA."""

        return self.get_queryset().esma()

    def bloomberg(self):
        """Return ratings that should be sent to Bloomberg."""
        return self.get_queryset().public_ratings(). \
            published_today().order_by('date_time_published',)

    # Current ratings
    def valid_decisions(self):
        """Show the last and currently valid rating decision."""
        return self.get_queryset().valid_decisions()

    def current_rating(self, issuer):
        """Show the last and currently valid rating decision."""
        return self.get_queryset().valid_decisions().\
            select_related('rating_type').get(issuer=issuer,
                                              is_current=True,)

    def rating_history(self):
        """Show the historical rating decisions ."""
        return self.get_queryset().valid_decisions().order_by(
            '-date_time_published').select_related('primary_analyst').\
            select_related('secondary_analyst')

    # Error management
    def has_confirmed_chair(self):
        """Return all records where chair is confirmed."""
        return self.base_filter().has_confirmed_chair()

    def has_confirmed_date(self):
        """Return all records where date is confirmed."""
        return self.base_filter().has_confirmed_date()

    def has_passed_committee_date(self):
        """Return all records where date and time for
        rating committee has been passed."""
        return self.base_filter().has_passed_committee_date()

    def missing_date_time_committee(self):
        """Return all records where a date has not been proposed."""
        return self.base_filter().missing_date_time_committee()

    def date_time_committee_not_confirmed(self):
        """Return all records where a date has
        been proposed but not confirmed."""
        return self.base_filter().date_time_committee_not_confirmed()

    def chair_not_confirmed(self):
        return self.base_filter().chair_not_confirmed()

    def missing_chair(self):
        return self.base_filter().missing_chair()

    def confirmed_non_chair_members(self):
        return self.base_filter().confirmed_non_chair_members()

    ##############################################
    # Below here is some stuff for the new version
    def in_progress(self):
        return self.base_filter().in_progress()

    def in_committee(self):
        """All ratings that are submitted for the committee."""

        return self.base_filter().in_committee()

    def pre_committee_questions_answered(self):
        return self.base_filter().pre_committee_questions_answered()

    def analyst_final_approval_questions_answered(self):
        return self.base_filter().analyst_final_approval_questions_answered()

    def chair_final_approval_questions_answered(self):
        return self.base_filter().chair_final_approval_questions_answered()

    def publishing_questions_answered(self):
        return self.base_filter().publishing_questions_answered()

    def external_analysis(self):
        return self.base_filter().external_analysis()

    def external_public_analysis(self):
        return self.base_filter().external_public_analysis()

    def internal_analysis(self):
        return self.base_filter().internal_analysis()

    def has_editor(self):
        return self.base_filter().has_editor()

    def has_contact_person(self):
        return self.base_filter().has_contact_person()


class RatingDecision(BaseModel):
    """Describe the attributes of a rating decision
    Uses a custom manager."""

    objects = ProcessManager()
    history = HistoricalRecords()

    class Meta:
        """Meta class."""
        ordering = ['issuer', 'date_time_committee', '-date_time_creation']

    def __str__(self):
        if self.date_time_deleted:
            return_string = "Record deleted on {}".format(
                self.date_time_deleted,
            )
        elif self.date_time_published:
            return_string = "Rating for {} published on {} | " \
                            "Current rating: {} | '{}'/{}/{}".format(
                                self.issuer,
                                self.date_time_published.strftime('%Y-%m-%d'),
                                self.is_current,
                                self.get_decided_lt_display(),
                                self.get_decided_lt_outlook_display(),
                                self.get_decided_st_display())
        else:
            return_string = "Rating job for {} | {} | Current rating: {}".\
                format(
                    self.issuer,
                    self.get_process_step_display(),
                    self.is_current,)

        return return_string

    @property
    def identifier(self):
        """Internal identifier for this rating job.
        Same as in template_tags."""

        return 'R' + str(self.pk).zfill(12)

    @property
    def has_passed_committee_date(self):
        """Set a flag if we're passed the committee date."""
        if self in RatingDecision.objects.has_passed_committee_date():
            return True
        else:
            return False

    @property
    def error_messages(self):
        """Return a list of errors for the rating decision."""

        self.error_list = []

        if self.get_process_step_display() == 'setup':

            if self in RatingDecision.objects.missing_date_time_committee():
                self.error_list.append('No date and time suggested.')

            if self in RatingDecision.objects.missing_chair():
                self.error_list.append('No chair proposed.')

        elif self.get_process_step_display() == 'pre_committee':

            if self in RatingDecision.objects.missing_date_time_committee():
                self.error_list.append('No date and time suggested.')

            if self in RatingDecision.objects.\
                    pre_committee_questions_answered():
                self.error_list.append('Not all questions answered.')

        elif self.get_process_step_display() == 'analytical_phase':

            if not self.proposed_lt:
                self.error_list.append('Recommend long-term rating')

            if not self.proposed_lt_outlook:
                self.error_list.append('Recommend outlook')

            if not self.proposed_st:
                self.error_list.append('Recommend short-term rating')

            if not self.event:
                self.error_list.append('Describe what events drives the '
                                       'rating.')

            if not self.recommendation_rationale:
                self.error_list.append('Write a rationale for the rating.')

            if timezone.now() + timedelta(hours=24) > \
                    self.date_time_committee:
                        self.error_list.append('You have missed the deadline '
                                               'for submission to the '
                                               'committee.')

            if self not in RatingDecision.objects.external_analysis():
                self.error_list.append('Attach the external analysis.')

            if self not in RatingDecision.objects.internal_analysis():
                self.error_list.append('Attach the internal analysis.')

        elif self.get_process_step_display() == 'post_committee':

            if not self.decided_lt:
                self.error_list.append('Set final long-term rating')

            if not self.decided_lt_outlook:
                self.error_list.append('Set final outlook')

            if not self.decided_st:
                self.error_list.append('Set final short-term rating')

            if self not in RatingDecision.objects.external_analysis():
                self.error_list.append('Attach the external analysis.')

            if self not in RatingDecision.objects.internal_analysis():
                self.error_list.append('Attach the internal analysis.')

            if self not in RatingDecision.objects.has_editor():
                self.error_list.append('Add an editor.')

            if not self.committee_comments:
                self.error_list.append('Put in some committee comments.')

            if self not in RatingDecision.objects. \
                    has_passed_committee_date():
                        self.error_list.append('Rating committee date and '
                                               'time not passed yet.')

        elif self.get_process_step_display() == 'editor_phase':

            if self not in RatingDecision.objects.external_analysis():
                self.error_list.append('Attach the external analysis.')

            if self not in RatingDecision.objects.has_contact_person():
                    self.error_list.append('Add at least one contact person.')

        elif self.get_process_step_display() == 'issuer_confirmation_phase':

            pass

        elif self.get_process_step_display() == 'analyst_final_approval_phase':

            if self in RatingDecision.objects.\
                    analyst_final_approval_questions_answered():
                        self.error_list.append('Not all questions answered.')

            if self not in RatingDecision.objects.external_public_analysis():
                self.error_list.append('Attach the analysis that will be '
                                       'published externally.')

        elif self.get_process_step_display() == 'chair_final_approval_phase':

            if self in RatingDecision.objects.\
                    chair_final_approval_questions_answered():
                        self.error_list.append('Not all questions answered.')

        elif self.get_process_step_display() == 'publishing_phase':

            if self in RatingDecision.objects. \
                    publishing_questions_answered():
                        self.error_list.append('Not all questions answered.')

        else:
            self.error_list.append('Not implemented.')

        return self.error_list

    # Links bank to the previous rating (if any)
    previous_rating = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    is_current = models.BooleanField(
        db_index=True,
        default=False,
    )

    """Returns what stage of the process we are in. Order is
    important in if clause. Later steps in process higher up
    in if-clause.
    """
    process_step = models.IntegerField(
        choices=PROCESS_STEPS,
        db_index=True,
        blank=False,
        null=False,
        default=1,
    )

    # Required by ESMA. Must be unique over the life span
    # of a rating.
    esma_rating_identifier = models.IntegerField(
        blank=True,
        null=True,
    )

    initiated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rating_decision_initiated_by",
        null=True,
        blank=True
    )

    # Link back to the Issuer
    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
        related_name='rating_decision_issuer'
    )

    # Why is this rating decision initiated
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT
    )

    # What type of rating (public, private etc)
    rating_type = models.ForeignKey(
        RatingType,
        on_delete=models.PROTECT
    )

    # Is this a preliminary rating?
    is_preliminary = models.BooleanField(default=False)

    # Payment model
    is_unsolicited = models.BooleanField(default=False)

    # What is the reason for the proposed rating?
    event = HTMLField(
        blank=True,
        null=True,
    )

    # On what date and time was the committee held
    date_time_committee = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # Has the proposed date been confirmed?
    date_time_committee_confirmed = models.BooleanField(default=False)

    # On what date and time was the rating published
    date_time_published = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # On what date and time was the preliminary rating
    # communicated to the issuer
    # Required by ESMA
    date_time_communicated_issuer = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # On what date and time was the rating deleted (if applicable)
    # If the record was created errouneously we dont delete it,
    # but instead mark it as deleted to keep a history of actions.
    date_time_deleted = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # When was the rating decision initiated?
    date_time_creation = models.DateTimeField(
        db_index=True,
        auto_now_add=True,
    )

    # What long-term rating does the analyst propose?
    proposed_lt = models.IntegerField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    # What long-term rating outlook does the analyst propose?
    proposed_lt_outlook = models.IntegerField(
        choices=RATING_LONG_TERM_OUTLOOK_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    # What short -term rating does the analyst propose?
    proposed_st = models.IntegerField(
        choices=RATING_SHORT_TERM_TUPLE,
        null=True,
        blank=True
    )

    # What long-term rating did the rating committee decide?
    decided_lt = models.IntegerField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    # What long-term rating outlook did the rating committee decide?
    decided_lt_outlook = models.IntegerField(
        choices=RATING_LONG_TERM_OUTLOOK_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    # What short -term rating did the rating committee decide?
    decided_st = models.IntegerField(
        choices=RATING_SHORT_TERM_TUPLE,
        null=True,
        blank=True
    )

    # Who was the chair during the meeting
    chair = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rating_decision_chair",
        null=True,
        blank=True
    )

    # Has the chair confirmed its chairmanship?
    chair_confirmed = models.BooleanField(default=False)

    # Who was primary analyst for the analysis
    primary_analyst = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rating_decision_primary_analyst",
        null=True,
        blank=True
    )

    # Who was secondary analyst for the analysis
    secondary_analyst = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rating_decision_secondary_analyst",
        null=True,
        blank=True
    )

    # Why do we make the recommentation?
    recommendation_rationale = HTMLField(
        null=True,
        blank=True,
    )

    # Any comments written by the committee goes here
    committee_comments = HTMLField(
        null=True,
        blank=True,
    )


@receiver(post_save, sender=RatingDecision)
def rating_decision_setup(sender, instance, created, **kwargs):
    """Adds a reference to the last valid decision upon creation."""

    if created:
        try:

            previous_decision_obj = RatingDecision.objects.current_rating(
                issuer=instance.issuer)

            instance.previous_rating = previous_decision_obj

            esma_identifier = previous_decision_obj.esma_rating_identifier

        except RatingDecision.DoesNotExist:
            # This is the first rating in the series, set identifier
            # to currekt pk
            esma_identifier = instance.pk

        instance.esma_rating_identifier = esma_identifier

        instance.save()
