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


class CountryRegion(Base):
    """Reflect the table."""

    __table__ = Table('countryregion',
                      Metadata,
                      autoload=True,
                      schema='static')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:
            session.add(CountryRegion(
                id=r.id,
                name=r.name,
                iso_31661_alpha_2=r.iso_31661_alpha_2,
                iso_31661_alpha_3=r.iso_31661_alpha_3,
                iso_31661_alpha_3_country_code=r.
                iso_31661_alpha_3_country_code,
                iso_3166_2=r.iso_3166_2,
                region=r.region,
                sub_region=r.sub_region,
                intermediate_region=r.intermediate_region,
                region_code=r.region_code,
                sub_region_code=r.sub_region_code,
                intermediate_region_code=r.intermediate_region_code,
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

        session.query(CountryRegion).delete()
