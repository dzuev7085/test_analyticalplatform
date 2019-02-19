"""This file contains a base class used to make SQL-connections
in files outside of Django."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SQL:
    """Class to connect to a Postgres database."""

    def __init__(self, database='DWH', debug=False):
        """Init class."""
        self.database_name = database
        self.quoted_string = None
        self._echo = debug

    @property
    def connection_string(self):
        """Create a connectioon string."""
        return "postgresql+psycopg2://%s:%s@%s:%s/%s" % \
               (os.environ['DB_USER'],
                os.environ['DB_PASSWORD'],
                os.environ['DB_HOST'],
                os.environ['DB_PORT'],
                self.database_name)

    @property
    def engine(self):
        """Create an engine."""
        return create_engine(self.connection_string,
                             echo=self._echo)

    @property
    def session(self):
        """Setup a session."""
        sql_session = sessionmaker()
        sql_session.configure(bind=self.engine)
        return sql_session()
