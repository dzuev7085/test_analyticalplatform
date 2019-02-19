from django.apps import AppConfig


class CreditAssessmentConfig(AppConfig):
    name = 'credit_assessment'

    def ready(self):

        # Initiate all signals in app
        import credit_assessment.signals  # noqa: F401
