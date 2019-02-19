"""Tasks to copy data to the entity table in the company schema."""
from celery import shared_task
from celery.utils.log import get_task_logger
from issuer.models import Issuer
from datalake.company.entity import Entity

logger = get_task_logger(__name__)


def refresh_issuer():
    """Helper function to refresh all issuer data from AP."""

    # Delete all records
    Entity.delete_all_data()

    # Get all objects in static database
    d = Issuer.objects.all()

    # Pass all data to insert function
    Entity.populate_data(d)


@shared_task
def populate_data_task():
    """Task to refresh all issuer data from AP."""

    refresh_issuer()
