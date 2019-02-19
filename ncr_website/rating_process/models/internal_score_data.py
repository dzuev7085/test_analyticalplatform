from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from pycreditrating.const import BASE_SCORE, RATING_LONG_TERM
from pycreditrating import Rating as PCRRating, factor_weight
from .rating_decision import RatingDecision
from .rating_decision_issue import RatingDecisionIssue
from simple_history.models import HistoricalRecords
from rating_process.util import generate_rating_dict


NOTCH_CHOICES = (
    (5, '+5'),
    (4, '+4'),
    (3, '+3'),
    (2, '+2'),
    (1, '+1'),
    (0, '0'),
    (-1, '-1'),
    (-2, '-2'),
    (-3, '-3'),
    (-4, '-4'),
    (-5, '-5'),
)


def create_score_data_point(rating_decision,
                            last_rating_decision,
                            subfactor_id,
                            weight,
                            is_assessment=False,):
    """Create a dict for score values to be inserted into database."""

    weight_edit_allowed = False

    try:

        try:
            data = InternalScoreData.objects.get(
                subfactor_id=subfactor_id,
                rating_decision=last_rating_decision)

        except ValueError:

            # Has to be imported here
            from credit_assessment.models.subscores import (
                AssessmentSubscoreData
            )

            # We're creating the data point based on an assessment
            try:
                data = AssessmentSubscoreData.objects.get(
                    subfactor_id=subfactor_id,
                    assessment=last_rating_decision)

                score = data.decided_score

            except AssessmentSubscoreData.DoesNotExist:
                score = None

        if weight is None:
            weight = data.weight
            weight_edit_allowed = True

    except InternalScoreData.DoesNotExist:

        # Set #n/a as default score
        score = None

        if weight is None:
            if subfactor_id == 12:
                weight = 0.1
            elif subfactor_id == 13:
                weight = 0.1
            elif subfactor_id == 17:
                weight = 0.075
            elif subfactor_id == 18:
                weight = 0.025

            weight_edit_allowed = True

    if is_assessment:
        return_dict = {'assessment': rating_decision,
                       'subfactor_id': subfactor_id,
                       'weight': weight,
                       'decided_score': score,
                       'weight_edit_allowed': weight_edit_allowed}
    else:
        return_dict = {'rating_decision': rating_decision,
                       'subfactor_id': subfactor_id,
                       'weight': weight,
                       'proposed_score': score,
                       'decided_score': score,
                       'weight_edit_allowed': weight_edit_allowed}

    return return_dict


def create_notch_data_point(rating_decision,
                            last_rating_decision,
                            subfactor_id,
                            is_assessment=False,):
    """Create a dict for score values to be inserted into database."""

    try:

        try:
            notch = InternalScoreData.objects.get(
                subfactor_id=subfactor_id,
                rating_decision=last_rating_decision).decided_notch_adjustment

        except ValueError:

            # Has to be imported here
            from credit_assessment.models.subscores import (
                AssessmentSubscoreData
            )

            # We're creating the data point based on an assessment
            try:
                notch = AssessmentSubscoreData.objects.get(
                    subfactor_id=subfactor_id,
                    assessment=last_rating_decision).decided_notch_adjustment

            except AssessmentSubscoreData.DoesNotExist:
                notch = 0

    except InternalScoreData.DoesNotExist:
        notch = 0

    if is_assessment:
        return {'assessment': rating_decision,
                'subfactor_id': subfactor_id,
                'decided_notch_adjustment': notch}
    else:
        return {'rating_decision': rating_decision,
                'subfactor_id': subfactor_id,
                'proposed_notch_adjustment': notch,
                'decided_notch_adjustment': notch}


def create_subscore_list(last_rating_decision, instance, issuer_type_id,
                         is_assessment=False,):
    """Create a list of sub scores that are created when a RatingJob or
    AssessmentJob is initiated."""

    # These risk factors are common for all type of issuers
    data = [
        # Peer comparison
        create_notch_data_point(instance,
                                last_rating_decision,
                                8,
                                is_assessment=is_assessment,),

        # Ownership support
        create_notch_data_point(instance,
                                last_rating_decision,
                                9,
                                is_assessment=is_assessment,),
    ]

    # These risk factors are common for both corporate and real estate
    if issuer_type_id == 1 or issuer_type_id == 3:
        # Operating environment
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            1,
            factor_weight(
                issuer_type_id,
                'business_risk_assessment',
                'operating_environment'),
            is_assessment=is_assessment), )

        # Operating efficiency
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            3,
            factor_weight(
                issuer_type_id,
                'business_risk_assessment',
                'operating_efficiency'),
            is_assessment=is_assessment,)
        )

        # Ratio analysis
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            27,
            factor_weight(
                issuer_type_id,
                'financial_risk_assessment',
                'ratio_analysis',
                version=2),
            is_assessment=is_assessment),
        )

        # Ratio analysis
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            28,
            factor_weight(
                issuer_type_id,
                'financial_risk_assessment',
                'risk_appetite',
                version=2),
            is_assessment=is_assessment),
        )

        # Liquidity
        data.append(create_notch_data_point(
            instance,
            last_rating_decision,
            6,
            is_assessment=is_assessment,))

        # ESG
        data.append(create_notch_data_point(
            instance,
            last_rating_decision,
            7,
            is_assessment=is_assessment,))

    # Corporate issuer
    if issuer_type_id == 1:

        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            2,
            factor_weight(
                issuer_type_id,
                'business_risk_assessment',
                'market_position'),
            is_assessment=is_assessment,))

        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            4,
            factor_weight(
                issuer_type_id,
                'business_risk_assessment',
                'size_diversification'),
            is_assessment=is_assessment,))

    # Financial
    elif issuer_type_id == 2:

        # National factors
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            12,
            None,
            is_assessment=is_assessment,))

        # Regional, cross border, sector
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            13,
            None,
            is_assessment=is_assessment,))

        # Capital
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            14,
            factor_weight(
                issuer_type_id,
                'risk_appetite',
                'capital'),
            is_assessment=is_assessment,))

        # Funding and liquidity
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            15,
            factor_weight(
                issuer_type_id,
                'risk_appetite',
                'funding_liquidity'),
            is_assessment=is_assessment,))

        # Risk governance
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            16,
            factor_weight(
                issuer_type_id,
                'risk_appetite',
                'risk_governance'),
            is_assessment=is_assessment,))

        # Credit risk
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            17,
            None,
            is_assessment=is_assessment,))

        # Market risk
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            18,
            None,
            is_assessment=is_assessment,))

        # Other risks
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            19,
            factor_weight(
                issuer_type_id,
                'risk_appetite',
                'other_risk'),
            is_assessment=is_assessment,))

        # Market position
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            20,
            factor_weight(
                issuer_type_id,
                'competitive_position',
                'market_position'),
            is_assessment=is_assessment,))

        # Earnings
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            21,
            factor_weight(
                issuer_type_id,
                'performance_indicator',
                'earnings'),
            is_assessment=is_assessment,))

        # Loss performance
        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            22,
            factor_weight(
                issuer_type_id,
                'performance_indicator',
                'loss_performance'),
            is_assessment=is_assessment,))

        # Transitions
        data.append(create_notch_data_point(instance,
                                            last_rating_decision,
                                            23,
                                            is_assessment=is_assessment,))

        # Borderline assessments
        data.append(create_notch_data_point(instance,
                                            last_rating_decision,
                                            24,
                                            is_assessment=is_assessment,))

        # Material credit enhancement
        data.append(create_notch_data_point(instance,
                                            last_rating_decision,
                                            25,
                                            is_assessment=is_assessment,))

        # Rating caps
        data.append(create_notch_data_point(instance,
                                            last_rating_decision,
                                            26,
                                            is_assessment=is_assessment,))

    # Corporate real estate issuer
    elif issuer_type_id == 3:

        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            10,
            factor_weight(
                issuer_type_id,
                'business_risk_assessment',
                'market_position_size_diversification'),
            is_assessment=is_assessment,))

        data.append(create_score_data_point(
            instance,
            last_rating_decision,
            11,
            factor_weight(
                issuer_type_id,
                'business_risk_assessment',
                'portfolio_assessment'),
            is_assessment=is_assessment,))

    return data


class InternalScoreDataFactor(models.Model):
    """What sub score parameters are there?"""

    def __str__(self):
        return '%s' % self.name

    name = models.CharField(
        max_length=128,
        blank=False,
        db_index=True,
        null=False
    )


class InternalScoreDataSubfactor(models.Model):
    """What sub score parameters are there?"""

    def __str__(self):
        return '%s: %s (order: %s)' % (
            self.factor,
            self.name,
            self.sort_order
        )

    # Link back to InternalScoreDataParameter
    factor = models.ForeignKey(
        InternalScoreDataFactor,
        on_delete=models.PROTECT,
    )

    name = models.CharField(
        max_length=128,
        blank=False,
        null=False
    )

    # If we want to order the appearance of the factor, use this field
    sort_order = models.IntegerField(
        db_index=True,
        null=True,
        blank=True
    )


class InternalScoreData(models.Model):
    """Describe the attributes of a risk subfactor score"""

    # Add version history to the model
    history = HistoricalRecords()

    class Meta:
        """Meta class."""
        ordering = ['rating_decision__issuer',
                    'rating_decision',
                    'subfactor__factor',
                    'subfactor']

    def __str__(self):
        if self.weight:
            return "{} ||| {} has been assigned rating '{}.'".format(
                       self.rating_decision,
                       self.subfactor,
                       self.get_proposed_score_display(),
                       self.rating_decision.date_time_committee)
        else:
            return "{} ||| {} has been assigned adjustment '{}.'".format(
                       self.rating_decision,
                       self.subfactor,
                       self.get_proposed_notch_adjustment_display(),
                       self.rating_decision.date_time_committee)

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    # Link back to InternalScoreDataSubFactor
    subfactor = models.ForeignKey(
        InternalScoreDataSubfactor,
        on_delete=models.PROTECT
    )

    weight = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )

    # May the user edit the field?
    weight_edit_allowed = models.BooleanField(default=False)

    # What is the score assigned to the parameter?
    proposed_score = models.IntegerField(
        choices=BASE_SCORE,
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        null=True,
        blank=True,
        default=False
    )

    # What is the score assigned to the parameter?
    decided_score = models.IntegerField(
        choices=BASE_SCORE,
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        null=True,
        blank=True,
        default=False
    )

    # How many notches is the rating affected (if applicable)
    proposed_notch_adjustment = models.IntegerField(
        choices=NOTCH_CHOICES,
        validators=[MinValueValidator(-10), MaxValueValidator(10)],
        null=True,
        blank=True,
        default=False
    )

    # How many notches is the rating affected (if applicable)
    decided_notch_adjustment = models.IntegerField(
        choices=NOTCH_CHOICES,
        validators=[MinValueValidator(-10), MaxValueValidator(10)],
        null=True,
        blank=True,
        default=False
    )


@receiver(post_save, sender=RatingDecision)
def create_rating_decision(sender, instance, created, **kwargs):
    """
    If we're adding the rating decision for a corporate,
    add all relevant data rows
    """
    if created:

        ############################################
        # Get last rating decision score so that the
        # analyst doesn't have to retype everything
        ############################################
        try:
            last_rating_decision = RatingDecision.objects.current_rating(
                issuer=instance.issuer)[0]
        except:  # noqa E722
            last_rating_decision = False

        issuer_type_id = instance.issuer.issuer_type.id

        # These risk factors are common for all type of issuers
        data = [
            # Peer comparison
            create_notch_data_point(instance,
                                    last_rating_decision,
                                    8),

            # Ownership support
            create_notch_data_point(instance,
                                    last_rating_decision,
                                    9),
        ]

        # These risk factors are common for both corporate and real estate
        if issuer_type_id == 1 or issuer_type_id == 3:

            # Operating environment
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                1,
                factor_weight(
                    issuer_type_id,
                    'business_risk_assessment',
                    'operating_environment')))

            # Operating efficiency
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                3,
                factor_weight(
                    issuer_type_id,
                    'business_risk_assessment',
                    'operating_efficiency')))

            # Financial risk assessment
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                5,
                factor_weight(
                    issuer_type_id,
                    'financial_risk_assessment',
                    'financial_risk_assessment')))

            # Liquidity
            data.append(create_notch_data_point(
                instance,
                last_rating_decision,
                6))

            # ESG
            data.append(create_notch_data_point(
                instance,
                last_rating_decision,
                7))

        # Corporate issuer
        if issuer_type_id == 1:

            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                2,
                factor_weight(
                    issuer_type_id,
                    'business_risk_assessment',
                    'market_position')))

            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                4,
                factor_weight(
                    issuer_type_id,
                    'business_risk_assessment',
                    'size_diversification')))

        # Financial
        elif issuer_type_id == 2:

            # National factors
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                12,
                None))

            # Regional, cross border, sector
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                13,
                None))

            # Capital
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                14,
                factor_weight(
                    issuer_type_id,
                    'risk_appetite',
                    'capital')))

            # Funding and liquidity
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                15,
                factor_weight(
                    issuer_type_id,
                    'risk_appetite',
                    'funding_liquidity')))

            # Risk governance
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                16,
                factor_weight(
                    issuer_type_id,
                    'risk_appetite',
                    'risk_governance')))

            # Credit risk
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                17,
                None))

            # Market risk
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                18,
                None))

            # Other risks
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                19,
                factor_weight(
                    issuer_type_id,
                    'risk_appetite',
                    'other_risk')))

            # Market position
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                20,
                factor_weight(
                    issuer_type_id,
                    'competitive_position',
                    'market_position')))

            # Earnings
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                21,
                factor_weight(
                    issuer_type_id,
                    'performance_indicator',
                    'earnings')))

            # Loss performance
            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                22,
                factor_weight(
                    issuer_type_id,
                    'performance_indicator',
                    'loss_performance')))

            # Transitions
            data.append(create_notch_data_point(instance,
                                                last_rating_decision,
                                                23))

            # Borderline assessments
            data.append(create_notch_data_point(instance,
                                                last_rating_decision,
                                                24))

            # Material credit enhancement
            data.append(create_notch_data_point(instance,
                                                last_rating_decision,
                                                25))

            # Rating caps
            data.append(create_notch_data_point(instance,
                                                last_rating_decision,
                                                26))

        # Corporate real estate issuer
        elif instance.issuer.issuer_type.id == 3:

            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                10,
                factor_weight(
                    issuer_type_id,
                    'business_risk_assessment',
                    'market_position_size_diversification')))

            data.append(create_score_data_point(
                instance,
                last_rating_decision,
                11,
                factor_weight(
                    issuer_type_id,
                    'business_risk_assessment',
                    'portfolio_assessment')))

        # Insert all rows created above
        for item in data:
            InternalScoreData.objects.create(**item)

        # Copy all seniority levels that were added in last rating decision
        try:
            last_rating_decision_issue_obj = \
                RatingDecisionIssue.objects.filter(
                    rating_decision=last_rating_decision)

            for row in last_rating_decision_issue_obj:
                RatingDecisionIssue.objects.create(
                    rating_decision=instance,
                    seniority=row.seniority,
                    proposed_lt=row.decided_lt,
                    decided_lt=row.decided_lt
                )

        except:  # noqa E722
            pass


@receiver(post_save, sender=InternalScoreData)
def update_long_term_rating(sender, instance, **kwargs):
    """Update the long term rating when a subscore is updated."""

    rating_decision_obj = instance.rating_decision

    issuer_type_id = rating_decision_obj.issuer.issuer_type.id

    internal_score_obj = InternalScoreData.objects.filter(
        rating_decision=rating_decision_obj
    ).all()

    try:
        # Return indicative ratings based on score input
        proposed_rating = PCRRating(generate_rating_dict(issuer_type_id,
                                                         internal_score_obj,
                                                         'proposed'))
        rating_decision_obj.proposed_lt = RATING_LONG_TERM[
            proposed_rating.issuer_assessment.upper()]

        # Return decided ratings based on score input
        decided_rating = PCRRating(generate_rating_dict(issuer_type_id,
                                                        internal_score_obj,
                                                        'decided'))

        rating_decision_obj.decided_lt = RATING_LONG_TERM[
            decided_rating.issuer_assessment.upper()]

        rating_decision_obj.primary_analyst = \
            instance.rating_decision.issuer.analyst.primary_analyst
        rating_decision_obj.secondary_analyst = \
            instance.rating_decision.issuer.analyst.secondary_analyst

        rating_decision_obj.save()

    except:  # noqa E722

        pass
