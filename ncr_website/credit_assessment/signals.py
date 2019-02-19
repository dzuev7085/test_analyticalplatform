from credit_assessment.models.assessment import AssessmentJob
from credit_assessment.models.subscores import AssessmentSubscoreData
from credit_assessment.models.seniority_level_assessment import (
    SeniorityLevelAssessment
)
from credit_assessment.models.highest_lowest import HighestLowest
from django.db.models.signals import post_save
from django.dispatch import receiver
from rating_process.models.internal_score_data import create_subscore_list


@receiver(post_save, sender=AssessmentJob)
def create_rating_assessment(sender, instance, created, **kwargs):
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
            last_rating_assessment = AssessmentJob.objects.get(
                issuer=instance.issuer,
                is_current=True,
            )

            instance.previous_assessment = last_rating_assessment
            instance.assessment_lt = last_rating_assessment.assessment_lt
            instance.comment = last_rating_assessment.comment

        except AssessmentJob.DoesNotExist:
            last_rating_assessment = False

        issuer_type_id = instance.issuer.issuer_type.id

        # Create a list of data relevant for the issuer type
        data = create_subscore_list(
            last_rating_assessment,
            instance,
            issuer_type_id,
            is_assessment=True,
        )

        # Insert all rows created above
        for item in data:
            AssessmentSubscoreData.objects.create(**item)

        instance.save()


@receiver(post_save, sender=AssessmentJob)
def create_rating_assessment_seniority(sender, instance, created, **kwargs):
    """
    If we're adding the rating decision for a corporate,
    add all relevant data rows
    """
    if created:

        if instance.issuer.issuer_type.id in [1, 3]:

            # Senior secured
            SeniorityLevelAssessment.objects.create(
                assessment=instance,
                seniority_id=2,
            )

        elif instance.issuer.issuer_type.id == 2:

            # Senior non-preferred
            SeniorityLevelAssessment.objects.create(
                assessment=instance,
                seniority_id=3,
            )

            # AT1
            SeniorityLevelAssessment.objects.create(
                assessment=instance,
                seniority_id=5,
            )

        # Senior unsecured
        SeniorityLevelAssessment.objects.create(
            assessment=instance,
            seniority_id=1,
        )

        # Subordinated
        SeniorityLevelAssessment.objects.create(
            assessment=instance,
            seniority_id=4,
        )


@receiver(post_save, sender=AssessmentJob)
def credit_highest_lowest(sender, instance, created, **kwargs):
    """If we're adding the rating assessment for a also add model for
    highest and lowest ratings."""

    if created:

        # Senior unsecured
        HighestLowest.objects.create(
            assessment=instance,
        )
