"""Queries for Google Analytics."""
from integrations.google.analytics.const import (
    START_DATE,
    END_DATE,
)


# ID number to the external web site account
VIEW_ID = 'ga:178547141'


UNIQUE_PAGEVIEWS = {
    "reportRequests": [
        {
            "viewId": VIEW_ID,
            "pageSize": 10000,
            "dateRanges": [
                {
                    "startDate": START_DATE,
                    "endDate": END_DATE
                }
            ],
            "metrics": [
                {
                    "expression": "ga:uniquePageviews"
                }
            ],
            "dimensions": [
                {"name": "ga:date"},
                {"name": "ga:pagePath"},

                {"name": "ga:country"},
                {"name": "ga:countryIsoCode"},
                {"name": "ga:region"},
                {"name": "ga:city"},
            ]
        }
    ]
}

UNIQUE_EVENTS = {
    "reportRequests": [
        {
            "viewId": VIEW_ID,
            "pageSize": 10000,
            "dateRanges": [
                {
                    "startDate": START_DATE,
                    "endDate": END_DATE
                }
            ],
            "metrics": [
                {
                    "expression": "ga:uniqueEvents"
                }
            ],
            "dimensions": [
                {"name": "ga:date"},
                {"name": "ga:eventLabel"},

                {"name": "ga:country"},
                {"name": "ga:countryIsoCode"},
                {"name": "ga:region"},
                {"name": "ga:city"},
            ]
        }
    ]
}

TOTAL_USERS = {
    "reportRequests": [
        {
            "viewId": VIEW_ID,
            "pageSize": 10000,
            "dateRanges": [
                {
                    "startDate": START_DATE,
                    "endDate": END_DATE
                }
            ],
            "metrics": [
                {
                    "expression": "ga:users"
                }
            ],
            "dimensions": [
                {"name": "ga:date"},
                {"name": "ga:pagePath"},

                {"name": "ga:country"},
                {"name": "ga:countryIsoCode"},
                {"name": "ga:region"},
                {"name": "ga:city"},
            ]
        }
    ]
}
