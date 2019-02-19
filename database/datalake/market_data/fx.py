"""Create all the tables in the static schema and tables for FX."""
from sqlalchemy import MetaData, Table, func
from sqlalchemy.ext.declarative import declarative_base
from datalake import DB_CONNECTION
from dateutil import parser
from datetime import datetime, timedelta

Base = declarative_base()

meta = MetaData()
engine = DB_CONNECTION.engine
session = DB_CONNECTION.session
Metadata = MetaData(bind=engine)
Base.metadata = Metadata


class FX(Base):
    """Reflect the table."""

    __table__ = Table('fx',
                      Metadata,
                      autoload=True,
                      schema='market_data')

    @classmethod
    def get_start_date(cls, from_ccy, to_ccy):
        """Get the start date to query external data from."""

        # Data should be pulled from at least 1980-01-01
        initial_start_date = parser.parse("1980-01-01")

        start_date = session.query(func.max(FX.report_date)).filter(
            cls.from_ccy == from_ccy,
            cls.to_ccy == to_ccy).one()[0]

        # Convert date in database to datetime object
        if start_date:
            start_date = datetime.combine(start_date, datetime.min.time())
        else:
            start_date = initial_start_date

        # Get the latest of the initial date and the date stored in the db
        date_list = [initial_start_date, start_date]
        use_start_date = max(date_list) + timedelta(days=1)

        return use_start_date

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:

            session.add(FX(
                report_date=r['report_date'].strftime('%Y-%m-%d'),
                from_ccy=r['from_ccy'],
                to_ccy=r['to_ccy'],
                value=r['value'],
                source=r['source'],
            ))

        try:
            session.commit()

        except Exception:
            # Commit didn't work, roll back transaction
            # to make sure there will be no future errors.

            session.rollback()
