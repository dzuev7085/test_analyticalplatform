"""This module tests the feedback sent by ESMA."""
from integrations.esma.utils.parse_feedback_files import parse_feedback_file
from django.test import TestCase


WARNING_XML = """<?xml version="1.0" encoding="UTF-8"?>

<fdb:FeedBackFileInfo xmlns:fdb="urn:publicid:ESMA:CRA3:FDBCRA:V1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dtypes="urn:publicid:ESMA:CRA3:DATATYPES:V1.2" ESMACRACode="CRA3T" Version="1.2" CreationDateAndTime="2018-11-19T07:33:31Z" xsi:schemaLocation="urn:publicid:ESMA:CRA3:FDBCRA:V1.2 CRA3_FDBCRA1.2.xsd">
  <fdb:OriginalFileName>NCRNO_DATRXX_CRA3T_001499_18.zip</fdb:OriginalFileName>
  <fdb:ErrorsInfo>
    <fdb:ContentRatingRecords>
      <fdb:ContentRatingErrorWarning>
        <dtypes:RecordReportingType>N</dtypes:RecordReportingType>
        <dtypes:WarningErrorType>W</dtypes:WarningErrorType>
        <dtypes:RatingErrorWarningReference>EQU-098</dtypes:RatingErrorWarningReference>
        <dtypes:ErrorMessage>The Action communication date is less than 24 hours from the Action validity date.</dtypes:ErrorMessage>
        <dtypes:RatingRecordIdentifier>
          <dtypes:RatingActionRecordIdentifier>
            <dtypes:RatingIdentifier>R000000000011_L_IU000000000005</dtypes:RatingIdentifier>
            <dtypes:RatingActionIdentifier>RA00000000000000000000000000000000001215</dtypes:RatingActionIdentifier>
          </dtypes:RatingActionRecordIdentifier>
        </dtypes:RatingRecordIdentifier>
      </fdb:ContentRatingErrorWarning>
    </fdb:ContentRatingRecords>
  </fdb:ErrorsInfo>
</fdb:FeedBackFileInfo>
"""

ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>

<fdb:FeedBackFileInfo xmlns:fdb="urn:publicid:ESMA:CRA3:FDBCRA:V1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dtypes="urn:publicid:ESMA:CRA3:DATATYPES:V1.2" ESMACRACode="CRA3T" Version="1.2" CreationDateAndTime="2018-11-22T19:31:36Z" xsi:schemaLocation="urn:publicid:ESMA:CRA3:FDBCRA:V1.2 CRA3_FDBCRA1.2.xsd">
  <fdb:OriginalFileName>NCRNO_DATRXX_CRA3T_000020_18.zip</fdb:OriginalFileName>
  <fdb:ErrorsInfo>
    <fdb:ContentRatingRecords>
      <fdb:ContentRatingErrorWarning>
        <dtypes:RecordReportingType>N</dtypes:RecordReportingType>
        <dtypes:WarningErrorType>E</dtypes:WarningErrorType>
        <dtypes:RatingErrorWarningReference>EQU-090</dtypes:RatingErrorWarningReference>
        <dtypes:ErrorMessage>You have reported an Action type NW for rating R000000000020_L_IU000000000005 but the previous Rating action is not "PR". The Action types "NW" can only be preceeded by a PR Action type.</dtypes:ErrorMessage>
        <dtypes:RatingRecordIdentifier>
          <dtypes:RatingActionRecordIdentifier>
            <dtypes:RatingIdentifier>R000000000020_L_IU000000000005</dtypes:RatingIdentifier>
            <dtypes:RatingActionIdentifier>RA00000000000000000000000000000000001235</dtypes:RatingActionIdentifier>
          </dtypes:RatingActionRecordIdentifier>
        </dtypes:RatingRecordIdentifier>
      </fdb:ContentRatingErrorWarning>
    </fdb:ContentRatingRecords>
  </fdb:ErrorsInfo>
</fdb:FeedBackFileInfo>

"""

SUCCESS_XML = """<?xml version="1.0" encoding="UTF-8"?>

<fdb:FeedBackFileInfo xmlns:fdb="urn:publicid:ESMA:CRA3:FDBCRA:V1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dtypes="urn:publicid:ESMA:CRA3:DATATYPES:V1.2" ESMACRACode="CRA3T" Version="1.2" CreationDateAndTime="2018-11-26T08:01:15Z" xsi:schemaLocation="urn:publicid:ESMA:CRA3:FDBCRA:V1.2 CRA3_FDBCRA1.2.xsd">
  <fdb:OriginalFileName>NCRNO_DATQXX_CRA3T_000030_18.zip</fdb:OriginalFileName>
  <fdb:NoErrors>OK</fdb:NoErrors>
</fdb:FeedBackFileInfo>"""


class FeedbackFileUtilTest(TestCase):

    def test_success_xml(self):
        d = parse_feedback_file(SUCCESS_XML)

        self.assertEqual(d, 1)

    def test_warning_xml(self):

        d = parse_feedback_file(WARNING_XML)

        self.assertEqual(d, 1)

    def test_error_xml(self):
        d = parse_feedback_file(ERROR_XML)

        self.assertEqual(d, 0)
