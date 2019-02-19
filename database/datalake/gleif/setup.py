"""Create all the tables in the Global Lei (GLEIF) schema."""
import os

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from datalake import DB_CONNECTION


BASE = declarative_base()


class dimLEI(BASE):
    __tablename__ = 'dimlei'
    __table_args__ = {"schema": "gleif"}

    id = Column(Integer, primary_key=True)
    lei = Column(
        postgresql.CHAR(20),
        nullable=False,
        unique=True)

    entity = relationship(
        'dimEntity',
        backref=backref('dimLEI',
                        lazy='joined',
                        uselist=False)
    )

    registration = relationship(
        'dimRegistration',
        backref=backref('dimLEI',
                        lazy='joined',
                        uselist=False)
    )


class dimEntity(BASE):
    __tablename__ = 'dimentity'
    __table_args__ = {"schema": "gleif"}

    id = Column(Integer, primary_key=True)
    legalname = Column(
        postgresql.TEXT,
        nullable=True,
        unique=True
    )
    businessregisterentityid = Column(postgresql.TEXT, nullable=True)
    legaljurisdiction = Column(postgresql.TEXT, nullable=True)
    legalform = Column(postgresql.TEXT, nullable=True)
    entitystatus = Column(postgresql.TEXT, nullable=True)

    # Link back to parent, which is dimLEI
    _lei_id = Column(
        Integer,
        ForeignKey(dimLEI.id,
                   ondelete='CASCADE'),
        nullable=False
    )

    addresses = relationship(
        'dimAddress',
        backref=backref('dimEntity',
                        lazy='joined',
                        uselist=False)
    )


class dimAddress(BASE):
    __tablename__ = 'dimaddress'
    __table_args__ = {"schema": "gleif"}

    id = Column(Integer, primary_key=True)
    addresstype = Column(postgresql.TEXT, nullable=True)
    line1 = Column(postgresql.TEXT, nullable=True)
    city = Column(postgresql.TEXT, nullable=True)
    region = Column(postgresql.TEXT, nullable=True)
    country = Column(postgresql.TEXT, nullable=True)
    postalcode = Column(postgresql.TEXT, nullable=True)
    _entity_id = Column(
        Integer,
        ForeignKey('gleif.dimentity.id', ondelete='CASCADE'),
        nullable=False
    )


class dimRegistration(BASE):
    __tablename__ = 'dimregistration'
    __table_args__ = {"schema": "gleif"}

    id = Column(Integer, primary_key=True)
    initialregistrationdate = Column(postgresql.TIMESTAMP, nullable=True)
    lastupdatedate = Column(postgresql.TIMESTAMP, nullable=True)
    registrationstatus = Column(postgresql.TEXT, nullable=True)
    nextrenewaldate = Column(postgresql.TIMESTAMP, nullable=True)
    managinglou = Column(postgresql.CHAR(20), nullable=True)
    validationsources = Column(postgresql.TEXT, nullable=True)

    _lei_id = Column(
        Integer,
        ForeignKey('gleif.dimlei.id', ondelete='CASCADE'),
        nullable=False
    )


# Used for test runners in Gitlab
# Creates the database which our Django app is depending on
if os.environ['FAKE_DB_SETUP'] == '1':
    BASE.metadata.create_all(DB_CONNECTION.engine)
