"""Create all the tables in the static schema and tables for GICS."""
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from datalake import DB_CONNECTION

Base = declarative_base()

meta = MetaData()
engine = DB_CONNECTION.engine
session = DB_CONNECTION.session
Metadata = MetaData(bind=engine)
Base.metadata = Metadata


class GICSSector(Base):
    """Reflect the table."""

    __table__ = Table('gicssector',
                      Metadata,
                      autoload=True,
                      schema='static')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:
            session.add(GICSSector(
                id=r.id,
                code=r.code,
                name=r.name,
                valid_from=r.valid_from,
                valid_to=r.valid_to,
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

        session.query(GICSSector).delete()


class GICSIndustryGroup(Base):
    """Reflect the table."""

    __table__ = Table('gicsindustrygroup',
                      Metadata,
                      autoload=True,
                      schema='static')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:
            session.add(GICSIndustryGroup(
                id=r.id,
                _sector_id=r.sector.id,
                code=r.code,
                name=r.name,
                valid_from=r.valid_from,
                valid_to=r.valid_to,
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

        session.query(GICSIndustryGroup).delete()


class GICSIndustry(Base):
    """Reflect the table."""

    __table__ = Table('gicsindustry',
                      Metadata,
                      autoload=True,
                      schema='static')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:
            session.add(GICSIndustry(
                id=r.id,
                _industry_group_id=r.industry_group.id,
                code=r.code,
                name=r.name,
                valid_from=r.valid_from,
                valid_to=r.valid_to,
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

        session.query(GICSIndustry).delete()


class GICSSubIndustry(Base):
    """Reflect the table."""

    __table__ = Table('gicssubindustry',
                      Metadata,
                      autoload=True,
                      schema='static')

    @classmethod
    def populate_data(cls, data):
        """Method to insert a new row."""

        for r in data:
            session.add(GICSSubIndustry(
                id=r.id,
                _industry_id=r.industry.id,
                code=r.code,
                name=r.name,
                description=r.description,
                valid_from=r.valid_from,
                valid_to=r.valid_to,
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

        session.query(GICSSubIndustry).delete()
