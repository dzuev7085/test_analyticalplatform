from django.db import models
from django.utils import timezone
from django.db.models import Q

from a_helper.static_database_table.models.currency import Currency
from issuer.models import Issuer

from simple_history.models import HistoricalRecords

import datetime


TODAY = datetime.datetime.today()


class ProcessQuerySet(models.QuerySet):
    """ProcessQuerySet class."""

    def live_trades(self):
        """Return issues that have not matured."""
        return self.filter(maturity__gte=timezone.now()).order_by('maturity')

    def issue_list(self, issuer_id, disbursed_before):
        """Get all issues including current rating."""

        # Written as a raw query to be able to join in current decision
        sql = '''SELECT       CASE WHEN i.is_matured = True THEN 'Matured'
                                   ELSE 'Live' END AS status
                            , i.id
                            , i.isin
                            , i.name
                            , i.ticker
                            , i.disbursement
                            , i.maturity
                            , i.amount

                            , static_database_table_currency.
                              currency_code_alpha_3 as ccy

                            , issue_seniority.name AS seniority_lvl
                            , issue_program.name as program_name

                            , issd.is_current
                            , issd.decided_lt
                            , issd.process_step
                            , issd.date_time_committee

                            , issd_inpr.process_step as in_progress
                            , issd_inpr.id as in_progress_id
                            , issd_inpr.decided_lt as in_progress_decided_lt

                            , (SELECT       i_rdec.id
                               FROM         rating_process_ratingdecision
                                            AS i_rdec
                               INNER JOIN   rating_process_ratingdecisionissue
                                            AS i_rdi
                                 ON   1 = 1
                                 AND  i_rdi.rating_decision_id = i_rdec.id
                                 AND  i_rdi.seniority_id       = i.seniority_id
                               WHERE        1 = 1
                               AND          i_rdec.issuer_id = i.issuer_id
                               AND          i_rdec.is_current = True
                               AND          i_rdec.date_time_deleted IS NULL
                               ORDER BY     id DESC
                               LIMIT 1
                              ) AS current_issue_decision

                 FROM         issue_issue as i

                 LEFT JOIN    rating_process_issuedecision AS issd
                   ON  1 = 1
                   AND i.id = issd.issue_id
                   AND issd.is_current = True
                   AND issd.date_time_deleted IS NULL

                 LEFT JOIN    rating_process_issuedecision AS issd_inpr
                   ON  1 = 1
                   AND i.id = issd_inpr.issue_id
                   AND issd_inpr.is_current = False
                   AND issd_inpr.date_time_published IS NULL
                   AND issd_inpr.date_time_deleted IS NULL

                 LEFT OUTER JOIN static_database_table_currency
                   ON  1 = 1
                   AND i.currency_id = static_database_table_currency.id

                 INNER JOIN issue_seniority
                   ON  1 = 1
                   AND i.seniority_id = issue_seniority.id

                 INNER JOIN issue_program
                   ON  1 = 1
                   AND i.program_id = issue_program.id

                 WHERE 1=1
                   AND issuer_id = %s
                   AND i.disbursement <= %s

                 ORDER BY     CASE WHEN i.is_matured = True then 1
                                   ELSE 0 END
                            , issue_seniority.name
                            , issue_program.name
                            , i.maturity'''

        return self.raw(sql, [issuer_id, disbursed_before])

    def matures_today(self):
        """Return issues that matures today or earlier."""

        return self.filter(Q(maturity__lte=TODAY))


class ProcessManager(models.Manager):
    """ProcessManager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    def live_trades(self):
        """Return issues that have not matured."""
        return self.get_queryset().live_trades()

    def issue_list(self, issue_id, disbursed_before):
        """Return issues that have not matured."""
        return self.get_queryset().issue_list(issue_id, disbursed_before)

    def matures_today(self):
        """Return issues that matures today or earlier."""
        return self.get_queryset().matures_today()


class SeniorityLevel(models.Model):
    """SeniorityLevel class."""

    def __str__(self):
        return '%s' % self.name

    name = models.CharField(
        max_length=128,
        unique=True
    )

    description = models.CharField(
        max_length=128,
        unique=True
    )


class Seniority(models.Model):
    """Seniority class."""

    class Meta:
        """Meta class."""
        ordering = ['name']

    def __str__(self):
        return '%s' % self.name

    seniority_level = models.ForeignKey(
        SeniorityLevel,
        on_delete=models.PROTECT
    )

    name = models.CharField(
        max_length=90,
    )

    description = models.TextField(
        max_length=500,
        unique=True
    )

    start_date = models.DateField(
        default='2018-09-29',
        null=False,
        blank=False
    )

    end_date = models.DateField(
        default='2099-12-31',
        null=False,
        blank=False
    )


class Program(models.Model):
    """Seniority class."""

    class Meta:
        """Meta class."""
        ordering = ['name']

    def __str__(self):
        return '%s' % self.name

    name = models.CharField(
        max_length=90,
    )

    description = models.TextField(
        max_length=500,
    )

    start_date = models.DateField(
        default='2018-09-29',
        null=False,
        blank=False
    )

    end_date = models.DateField(
        default='2099-12-31',
        null=False,
        blank=False
    )


class Issue(models.Model):
    """Issue class."""

    # Add version history to the model
    history = HistoricalRecords()

    objects = ProcessManager()

    def __str__(self):
        return '{}: {} {} m'.format(
            self.isin,
            self.currency.currency_code_alpha_3,
            round(self.amount/1000000, 1)
        )

    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
        related_name="issue_issuer_link",
        null=False,
        blank=False
    )

    is_matured = models.BooleanField(
        db_index=True,
        default=False,
    )

    isin = models.CharField(
        max_length=12,
        unique=True
    )

    name = models.CharField(
        max_length=132,
        blank=True,
        null=True
    )

    ticker = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        null=True
    )

    disbursement = models.DateField(
        blank=True,
        null=True
    )

    maturity = models.DateField(
        db_index=True,
        blank=False,
        null=False
    )

    interest = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="issue_currency_link",
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        blank=True,
        null=True
    )

    seniority = models.ForeignKey(
        Seniority,
        on_delete=models.PROTECT,
        related_name="issue_seniority_link",
        null=False,
        blank=False
    )

    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )
