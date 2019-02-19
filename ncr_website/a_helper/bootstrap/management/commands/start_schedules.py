"""Setup a task that automatically updates the GLEIF registry
on a daily basis."""
from background_task.models import Task
from django.core.management.base import BaseCommand

from a_helper.scheduler.tasks import update_gleif


class Command(BaseCommand):
    """Command class to create scheduled tasks."""

    def handle(self, *args, **options):
        """Method setting up the default runners."""

        # Make sure there is only one runner for this model.
        if not Task.objects.filter(
                task_name='scheduler.tasks.update_gleif').exists():

            update_gleif(repeat=60 * 60 * 24,
                         verbose_name="Update the GLEIF registry")
