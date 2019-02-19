from pygleif import GLEIF
from sqlalchemy.sql import exists

from .setup import dimAddress, dimEntity, dimLEI, dimRegistration


class GLEIFData:

    def __init__(self, db_connection, LEI=None):
        """Initilize class."""

        self.lei_code = LEI
        self.db_connection = db_connection
        self.session = self.db_connection.session

    @property
    def list_lei(self):
        """
        Query the database for all LEI-codes
        :return: A list of LEI-codes
        """
        data = []
        for a in self.session.query(dimLEI.lei).all():
            data.append(a[0])

        return(data)

    @property
    def data(self):
        """Query the database for data on a LEI-code.
        Due to the unique property of LEI, this should
        return one and one row only. If not, something
        is wrong.
        :param LEI: the unique LEI code to be inserted or updated
        :return: An Object with all relevant LEI data.
        """
        # TODO: add addresses

        try:
            return (
                self.session.query(
                    dimLEI,
                    dimEntity,
                    dimRegistration
                )
                .join(dimLEI.entity)
                .join(dimLEI.registration)
                .filter(dimLEI.lei == self.lei_code)
                .one()
            )
        except Exception:
            return False

    @property
    def entity(self):

        if self.data:
            return self.data[0].entity[0]

    @property
    def registration(self):
        if self.data:
            return self.data[0].registration[0]

    @property
    def legal_address(self):

        if self.data:
            if self.entity.addresses[1].addresstype == 'LegalAddress':
                return self.entity.addresses[1]
            if self.entity.addresses[0].addresstype == 'LegalAddress':
                return self.entity.addresses[0]

    @property
    def hq_address(self):

        if self.data:
            if self.entity.addresses[1].addresstype == 'HeadquarterAddress':
                return self.entity.addresses[1]
            if self.entity.addresses[0].addresstype == 'HeadquarterAddress':
                return self.entity.addresses[0]

    @property
    def return_data(self):
        return (
            {
                'entity': self.entity,
                'registration': self.registration,
                'headquarter_address': self.hq_address,
                'legal_address': self.legal_address
            }
        )


class GLEIFEditor:

    def __init__(self, db_connection):
        """Initilize class."""

        self.db_connection = db_connection
        self.session = self.db_connection.session

    @property
    def data(self):
        """Query the database for data on a LEI-code.
        Due to the unique property of LEI, this should
        return one and one row only. If not, something
        is wrong.
        :param LEI: the unique LEI code to be inserted or updated
        :return: An Object with all relevant LEI data.
        """
        # TODO: add addresses

        return (
            self.session.query(
                dimLEI,
                dimEntity,
                dimRegistration
            )
            .join(dimLEI.entity)
            .join(dimLEI.registration)
            .filter(dimLEI.lei == self.lei_code)
            .one()
        )

    def upsert(self, LEI):
        """
        Insert new record, or update old record.
        :param LEI: the unique LEI code to be inserted or updated
        """
        self.lei_code = LEI

        if self.record_exists:
            # Update entity
            self.data.dimEntity.LegalName = self.api_data.entity.legal_name
            self.data.dimEntity.BusinessRegisterEntityID = \
                self.api_data.entity.business_register_entity_id
            self.data.dimEntity.LegalJurisdiction = \
                self.api_data.entity.legal_jurisdiction
            self.data.dimEntity.LegalForm = self.api_data.entity.legal_form
            self.data.dimEntity.EntityStatus = \
                self.api_data.entity.entity_status

            # TODO: add other stuff here too

        else:
            self.session.add(self.insert_stmnt_lei)

        self.session.commit()

    @property
    def record_exists(self):
        """
        Check if a LEI-code has already been inserted.
        :return: True if row exists, else False
        """
        return(
            self.session.query(
                exists().where(dimLEI.lei == self.lei_code)).scalar()
        )

    @property
    def api_data(self):
        """Query the GLEIF API
        :return: An object"""
        return GLEIF(self.lei_code)

    @property
    def insert_stmnt_address_legal(self):
        return (
            dimAddress(
                addresstype='LegalAddress',
                line1=self.api_data.entity.legal_address.line1,
                city=self.api_data.entity.legal_address.city,
                region=self.api_data.entity.legal_address.region,
                country=self.api_data.entity.legal_address.country,
                postalcode=self.api_data.entity.legal_address.postal_code,
                _entity_id=dimEntity.id
            )
        )

    @property
    def insert_stmnt_address_hq(self):
        return (
            dimAddress(
                addresstype='LegalAddress',
                line1=self.api_data.entity.headquarters_address.line1,
                city=self.api_data.entity.headquarters_address.city,
                region=self.api_data.entity.headquarters_address.region,
                country=self.api_data.entity.headquarters_address.country,
                postalcode=self.api_data.entity.headquarters_address.
                postal_code,
                _entity_id=dimEntity.id
            )
        )

    @property
    def insert_stmnt_entity(self):
        return(
            dimEntity(
                legalname=self.api_data.entity.legal_name,
                businessregisterentityid=self.
                api_data.entity.business_register_entity_id,
                legaljurisdiction=self.api_data.entity.legal_jurisdiction,
                legalform=self.api_data.entity.legal_form,
                entitystatus=self.api_data.entity.entity_status,
                _lei_id=dimLEI.id,
                addresses=[
                    self.insert_stmnt_address_hq,
                    self.insert_stmnt_address_legal
                ]
            )
        )

    @property
    def insert_stmnt_registration(self):
        return(
            dimRegistration(
                initialregistrationdate=self.api_data.registration.
                initial_registration_date,
                lastupdatedate=self.api_data.registration.last_update_date,
                registrationstatus=self.api_data.registration.
                registration_status,
                nextrenewaldate=self.api_data.registration.next_renewal_date,
                managinglou=self.api_data.registration.managing_lou,
                validationsources=self.api_data.registration.
                validation_sources,
                _lei_id=dimLEI.id
            )
        )

    @property
    def insert_stmnt_lei(self):
        return(
            dimLEI(
                lei=self.lei_code,
                entity=[self.insert_stmnt_entity],
                registration=[self.insert_stmnt_registration]
            )
        )
