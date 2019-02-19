"""This module contains questions that are asked during the rating process.
It also contains a model to link those questions to a rating decision job.
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .rating_decision import RatingDecision

from simple_history.models import HistoricalRecords


class Stage(models.Model):

    def __str__(self):
        return '%s' % self.name

    name = models.CharField(
        db_index=True,
        max_length=100,
        blank=False,
        null=False
    )


class Question(models.Model):
    """Model to represent the process that follows upon a rating decision
    that has been approved by the chair."""

    def __str__(self):
        return '%s | %s | %s' % (
            self.stage,
            self.is_enabled,
            self.question,
        )

    stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
    )

    is_enabled = models.BooleanField(default=False)

    question = models.CharField(
        db_index=True,
        max_length=255,
        blank=False,
        null=False
    )


class ControlQuestion(models.Model):
    """Model to link a question with a rating decision."""

    # Add version history to the model
    history = HistoricalRecords()

    class Meta:
        ordering = ('rating_decision', 'question__question',)

    def __str__(self):
        return '%s | %s | Answer: %s' % (
            self.rating_decision,
            self.question,
            self.answer_correct
        )

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    answered_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="control_question_answered_by",
        null=True,
        blank=True
    )

    # On what date and time was the rating published
    answered_on = models.DateTimeField(
        null=True,
        blank=True
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT
    )

    answer_correct = models.BooleanField(default=False)


@receiver(post_save, sender=RatingDecision)
def create_questions(sender, instance, created, **kwargs):
    """Create a process object whenever a rating decision
    object has been created."""

    if created:

        active_questions = Question.objects.filter(is_enabled=True)

        for row in active_questions:

            ControlQuestion.objects.create(rating_decision=instance,
                                           question=row)
