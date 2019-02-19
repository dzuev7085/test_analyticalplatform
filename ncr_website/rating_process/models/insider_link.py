from django.db import models

from issuer.models import InsiderList

from .rating_decision import RatingDecision


class RatingDecisionInsiderLink(models.Model):

    def __str__(self):
        return '%s %s (%s%s)' % (
            self.insider.first_name,
            self.insider.last_name,
            self.insider.role,
            ' | ' + self.insider.get_contact_type_display() if self.insider.
            contact_type else '')

    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    insider = models.ForeignKey(
        InsiderList,
        on_delete=models.PROTECT,
    )
