"""Create all the tables in the static schema and tables for Currency."""
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from datalake import DB_CONNECTION

Base = declarative_base()

meta = MetaData()
engine = DB_CONNECTION.engine
session = DB_CONNECTION.session
Metadata = MetaData(bind=engine)
Base.metadata = Metadata


class Currency(Base):
    """Reflect the table."""

    __table__ = Table('currency',
                      Metadata,
                      autoload=True,
                      schema='static')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:
            session.add(Currency(
                id=r.id,
                name=r.name,
                currency_code_alpha_3=r.currency_code_alpha_3,
                currency_code_alpha_3_currency_code=r.
                currency_code_alpha_3_currency_code
            ))

        try:
            session.commit()
        except Exception:
            # Commit didn't work, roll back transaction
            # to make sure there will be no future errors.

            session.rollback()

    @classmethod
    def delete_all_data(cls):
        """Deletes all data in the static table."""

        session.query(Currency).delete()
