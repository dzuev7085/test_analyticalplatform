class FDVMParameters:

    def __init__(self, db_connection, row_name, organisation_id, date):
        self.db = db_connection
        self.row_name = row_name
        self.organisation_id = organisation_id
        self.date = date

    @property
    def query_id_numbers(self):
        return "SELECT        dsr.ID AS statement_row_id " \
               "            , dsrt.ID AS statement_row_title_id " \
               "FROM          FDVM.dimStatement    AS ds " \
               "INNER JOIN    FDVM.dimStatementRow AS dsr " \
               "  ON 1 = 1 " \
               "    AND ds.ID = dsr._statementID " \
               "INNER JOIN    FDVM.dimStatementRowTitle AS dsrt " \
               "  ON 1 = 1 " \
               "    AND dsrt.ID = dsr._rowTitleID " \
               "WHERE dsrt.rowTitle = '%s'" % (self.row_name)

    @property
    def statement_id(self):
        result = self.db.query(self.query_id_numbers)
        return result[0]['statement_id']

    @property
    def statement_row_id(self):
        result = self.db.query(self.query_id_numbers)
        return result[0]['statement_row_id']

    def fact_statement_entry_exists(self):
        query = "SELECT COUNT(*) AS noRows " \
                "FROM DWH.FDVM.vw_financialData " \
                "WHERE _organisationID='%s' " \
                "AND rowTitle = '%s' " \
                "AND date = '%s'" % (self.organisation_id,
                                     self.row_name,
                                     self.date)
        result = self.db.query(query)
        return result[0]['noRows']

    def fact_statement_insert(self, value):
        query = "INSERT INTO DWH.FDVM.factStatement " \
                "(_organisationID, _statementRowID, date, value) " \
                "VALUES (%s, %s, %s, %s) " % (self.organisation_id,
                                              self.statement_row_id,
                                              self.date, value)
        self.db.query(query)

    def fact_statement_update(self, value):
        query = "UPDATE DWH.FDVM.factStatement " \
                "SET value = '%s' " \
                "WHERE _statementRowID = '%s' " \
                "AND _organisationID = '%s' " \
                "AND date = '%s'" % (value,
                                     self.statement_row_id,
                                     self.organisation_id,
                                     self.date)
        self.db.query(query)

    def store_value(self, value):
        if self.fact_statement_entry_exists:
            self.fact_statement_update(value)
        else:
            self.fact_statement_insert(value)
