"""Task to populate static data."""
from celery import shared_task
from celery.utils.log import get_task_logger
from a_helper.static_database_table.utils import (
    refresh_country_region,
    refresh_currency,
    refresh_gics
)

logger = get_task_logger(__name__)


@shared_task
def refresh_static_data():
    """Refresh static data."""

    # Refresh data for country and region
    refresh_country_region()
    logger.info("Refreshed static / countryregion.")

    # Refresh data for currency
    refresh_currency()
    logger.info("Refreshed static / currency.")

    # Refresh data for GICS
    refresh_gics()
    logger.info("Refreshed static / GICS data.")
