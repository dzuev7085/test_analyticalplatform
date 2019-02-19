import warnings
from pandasdmx import Request
from datalake.market_data.fx import FX
from celery.utils.log import get_task_logger
from dateutil import parser
from datetime import date as D, datetime
logger = get_task_logger(__name__)


# What unit is the currency quoted in
BASE_UNIT = {
    'SEK': 100,
    'USD': 1,
    'EUR': 1,
    'DKK': 100,
}
FROM_CCY = 'NOK'


def load_fx():
    """Load rates from the Norges Riksbank into the the datalake table."""

    # Create a request to Norges Bank
    nb = Request('NB')

    for currency in BASE_UNIT:
        unit = BASE_UNIT[currency]

        use_start_date = FX.get_start_date(
            FROM_CCY, currency)

        # Convert today to a datetime
        end_date = datetime.combine(D.today(), datetime.min.time())

        # Don't look again if we've already run the check today
        if use_start_date != end_date:

            start_period = use_start_date.strftime('%Y-%m-%d')

            # Define what currencies we're interested in
            key = dict(
                BASE_CUR=[currency],
                FREQ='B',
            )

            # Fetch data
            data_response = nb.data(
                resource_id='EXR',
                key=key,
                params={'startPeriod': start_period}
            )

            # Return data as pandas data frame
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = data_response.write(data_response.data.series,
                                         parse_time=False)

                for column in df:
                    save_values = []

                    to_ccy = df[column].name[1]

                    exchange_pair = ('{}/{}'.format(
                        FROM_CCY,
                        to_ccy
                    ))

                    for (date, value) in df[column].iteritems():

                        # Convert to datetime, as this is what the
                        # populate_data method below expects
                        date_datetime = parser.parse(date)

                        try:
                            value = value / unit

                            data = dict(
                                report_date=date_datetime,
                                from_ccy=FROM_CCY,
                                to_ccy=to_ccy,
                                value=value,
                                source='Norges Bank'
                            )

                            save_values.append(data)

                            log_data = '{} | {} | {}'.format(
                                exchange_pair,
                                date,
                                value,
                            )

                            # log what was added
                            logger.info(log_data)

                        except Exception as e:
                            print(e)
                            pass

                    try:
                        FX.populate_data((save_values))
                    except Exception as e:

                        logger.info(e)
