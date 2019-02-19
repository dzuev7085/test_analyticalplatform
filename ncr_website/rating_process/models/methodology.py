from django.db import models

from methodology.models import Methodology

from .rating_decision import RatingDecision


class RatingDecisionMethodologyLink(models.Model):

    def __str__(self):
        return 'Links %s and %s' % (self.rating_decision, self.methodology)

    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    methodology = models.ForeignKey(
        Methodology,
        on_delete=models.PROTECT,
    )
