"""Create all the tables in the Global Lei (GLEIF) schema."""
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from datalake import DB_CONNECTION

Base = declarative_base()

meta = MetaData()
engine = DB_CONNECTION.engine
session = DB_CONNECTION.session
Metadata = MetaData(bind=engine)
Base.metadata = Metadata


class FinancialStatement(Base):
    """Reflect the findata.financial_statement table."""

    __table__ = Table('financial_statement',
                      Metadata,
                      autoload=True,
                      schema='findata')

    @classmethod
    def update_row(cls, row_id, update_user, new_value):
        """Method to update a specific row."""

        session.query(FinancialStatement).filter(
            FinancialStatement.id == row_id).update(
            {'amount': new_value, 'updated_by': update_user})

        session.commit()

    @classmethod
    def insert_row(cls,
                   lei,
                   report_date,
                   report_date_type,
                   target_item,
                   currency,
                   new_value,
                   update_user,
                   data_source,
                   statement_type,):
        """Method to insert a new row."""

        session.add(FinancialStatement(
            lei=lei,
            report_date=report_date,
            report_date_type=report_date_type,
            target_item=target_item,
            source_item=target_item,
            updated_by=update_user,
            amount=new_value,
            currency=currency,
            data_source=data_source,
            statement_type=statement_type,
        ))

        try:
            session.commit()
        except Exception:
            # Commit didn't work, roll back transaction
            # to make sure there will be no future errors.

            session.rollback()
