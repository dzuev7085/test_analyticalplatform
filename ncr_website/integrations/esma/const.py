"""Constants for reporting to ESMA."""
import datetime

TODAY_DATE = datetime.datetime.utcnow().strftime('%Y-%m-%d')

NCR_LEI = '549300MLUDYVRQOOXS22'
NCR_HUB_RECIPIENT = 'CRA3T'

FILE_TYPE_LOOKUP = {
    'DATQXX': 1,
    'DATRXX': 2,
}

ROOT_RATING_DATA_REPORT = 'RatingDataReport'

FILE_TYPE_RATING_QUALITATIVE = 'DATQXX'
FILE_TYPE_RATING_QUANTITATIVE = 'DATRXX'

FILE_TYPE_FEE_QUALITATIVE = 'DATFQL'
FILE_TYPE_FEE_QUANTITATIVE = 'DATFQN'

ATTR_UPDATED_STR = 'Data changed'

YN_MAPPING = {
    False: 'N',
    True: 'Y'
}

YN_MAPPING_REVERSE = {
    'N': False,
    'Y': True
}

# How many days in the past to look for decisions?
LOOKBACK = 14

# For debug
ACTION_TYPE = {1: 'OR',
               2: 'PR',
               3: 'NW',
               4: 'UP',
               5: 'DG',
               6: 'AF',
               7: 'DF',
               8: 'SP',
               9: 'WD',
               10: 'OT',
               11: 'WR'}
