from django.contrib.auth.models import User
from django.db import models

from .rating_decision import RatingDecision


class ProcessQuerySet(models.QuerySet):

    def member_not_confirmed(self):
        """Check that the record is not confirmed."""
        return self.filter(
            committee_member_confirmed=False)

    def confirmed_members(self):
        """Check that the record is not confirmed."""
        return self.filter(
            committee_member_confirmed=True)


class ProcessManager(models.Manager):

    def get_queryset(self):
        """Basic query set."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    def member_not_confirmed(self):
        return self.get_queryset().member_not_confirmed()

    def confirmed_members(self):
        return self.get_queryset().confirmed_members()


class Role(models.Model):

    def __str__(self):
        return self.role_name

    role_name = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )


class Group(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )


class JobMember(models.Model):
    """Describe the attributes of a committee member
    for a specific decision."""

    objects = ProcessManager()

    def __str__(self):
        if self.committee_member_confirmed:
            return '%s is a confirmed %s for rating decision %s' % (
                self.member,
                self.role,
                self.rating_decision
            )
        else:
            return '%s is a %s for rating decision %s' % (
                self.member,
                self.role,
                self.rating_decision
            )

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT
    )

    # Who (what user) initiated the rating?
    member = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="committee_member_committee_member",
        null=True,
        blank=True
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    # Link back to the RatingDecision
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    # Has the member confirmed its attendance?
    committee_member_confirmed = models.BooleanField(
        db_index=True,
        default=False
    )
