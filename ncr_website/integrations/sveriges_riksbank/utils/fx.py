"""Module to load rates from the Swedish Riksbank."""
from zeep import Client
from datetime import date, datetime
from celery.utils.log import get_task_logger
from datalake.market_data.fx import FX

logger = get_task_logger(__name__)

WSDL = 'https://swea.riksbank.se/sweaWS/wsdl/sweaWS_ssl.wsdl'
client = Client(WSDL)

FOREIGN_RATES_GROUPID = 130

RATE_PAIRS = [
    'SEKEURPMI',
    'SEKUSDPMI',
    'SEKNOKPMI',
    'SEKDKKPMI'
]


def load_fx():
    """Load rates from the Swedish Riksbank into the the datalake table."""

    for pair in RATE_PAIRS:
        save_values = []

        lookup = dict(
            groupid=130,  # always 130
            seriesid=pair,
        )

        from_ccy = pair[0:3]
        to_ccy = pair[3:6]

        exchange_pair = ('{}/{}'.format(
            from_ccy,
            to_ccy
        ))

        # Get start date to start query from
        use_start_date = FX.get_start_date(from_ccy, to_ccy)

        # Convert today to a datetime
        end_date = datetime.combine(date.today(), datetime.min.time())

        # Don't look again if we've already run the check today
        if use_start_date != end_date:

            query = dict(languageid='en',
                         aggregateMethod='D',
                         avg=False,
                         min=False,
                         max=False,
                         ultimo=False,
                         datefrom=use_start_date,
                         dateto=end_date,
                         searchGroupSeries=lookup)

            result = client.service.getInterestAndExchangeRates(
                searchRequestParameters=query)

            # Some rates are quoted in other unit than 1
            unit = int(result['groups'][0]['series'][0]['unit'])

            for r in result['groups'][0]['series'][0]['resultrows']:

                try:
                    value = r['value']/unit

                    data = dict(
                        report_date=r['date'],
                        from_ccy=from_ccy,
                        to_ccy=to_ccy,
                        value=value,
                        source='Sveriges Riksbank'
                    )

                    save_values.append(data)

                    log_data = '{} | {} | {}'.format(
                        exchange_pair,
                        r['date'],
                        value,
                    )

                    # log what was added
                    logger.info(log_data)

                except Exception:
                    pass

            # Store all data in the database
            try:
                FX.populate_data((save_values))
            except Exception as e:

                logger.info(e)
