"""Tasks that are completely stand-alone from apps."""
import shutil
import os

from celery import shared_task
from celery.utils.log import get_task_logger

from issuer.models import Issuer
from datalake.gleif.command import GLEIFEditor, GLEIF

logger = get_task_logger(__name__)


@shared_task(autoretry_for=(Exception,),
             default_retry_delay=30,
             max_retries=10)
def delete_files_task(*args):
    """Delete files."""

    for arg in args:

        try:
            shutil.rmtree(arg)
        except Exception:

            try:
                os.remove(arg)
            except Exception:
                pass

        logger.info("Deleted " + str(arg))

    logger.info("Clean up successful")


@shared_task(autoretry_for=(Exception,),
             default_retry_delay=30,
             max_retries=10)
def sync_issuers():
    """Make sure all issuers in financial database also are in
    analytical platform."""

    from a_helper.other.sql import SQL
    from datalake.findata.tables import FinancialStatement

    # create database connection and session
    DB_DATALAKE = SQL('datalake')

    # What issuers are in system
    a = Issuer.objects.values_list('lei', flat=True)

    # Get list of lei not in system
    rs = DB_DATALAKE.session.query(
        FinancialStatement).distinct(
        FinancialStatement.lei).filter(
        ~FinancialStatement.lei.in_(a))

    for r in rs:
        logger.info("Adding {}".format(r.lei))
        print(r.lei)

        try:
            GLEIFEditor(DB_DATALAKE).upsert(r.lei)

            gleif_data = GLEIF(r.lei)
            legal_name = gleif_data.entity.legal_name

            if len(legal_name) > 0:

                Issuer.objects.create(
                    lei=r.lei,
                    relationship_manager_id=1,
                    issuer_type_id=2,
                    legal_name=gleif_data.entity.legal_name,
                )

        except Exception:
            pass
