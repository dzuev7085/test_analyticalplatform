"""Create all the tables in the static schema and tables for CountryRegion."""
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from datalake import DB_CONNECTION

Base = declarative_base()

meta = MetaData()
engine = DB_CONNECTION.engine
session = DB_CONNECTION.session
Metadata = MetaData(bind=engine)
Base.metadata = Metadata


class Entity(Base):
    """Reflect the table."""

    __table__ = Table('entity',
                      Metadata,
                      autoload=True,
                      schema='company')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:

            if r.gics_sub_industry is None:
                gics_sub_industry_id = None
            else:
                gics_sub_industry_id = r.gics_sub_industry.id

            if r.address.country is None:
                country_region_id = None
            else:
                country_region_id = r.address.country.id

            session.add(Entity(
                id=r.id,
                lei=r.identifier.lei,
                internal_identifier=r.internal_identifier,
                legal_name=r.legal_name,
                short_name=r.short_name,
                _gics_sub_industry_id=gics_sub_industry_id,
                _issuer_type_id=r.issuer_type.id,
                _country_region_id=country_region_id,
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

        try:
            session.query(Entity).delete()

        except Exception:

            session.rollback()

            try:
                session.query(Entity).delete()

            except Exception:

                session.rollback()
