"""Connect to to the Google API."""
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = service_account.Credentials.from_service_account_file(
        key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name,
                    api_version,
                    cache_discovery=False,
                    credentials=credentials)

    return service


def return_response(service, query):
    """Parses and outputs tje Analytics Reporting API V4 response as a
    Pandas dataframe.
    """

    response = service.reports().batchGet(body=query).execute()
#    from pprint import pprint
#    pprint(response)

    data = []

    for report in response.get('reports', []):
        column_header = report.get('columnHeader', {})
        dimension_headers = column_header.get('dimensions', [])
        metric_headers = column_header.get('metricHeader', {}).get(
            'metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            date_range_values = row.get('metrics', [])

            row_d = {}

            for header, dimension in zip(dimension_headers, dimensions):

                # Append dimensions to output row
                row_d[header] = dimension

            for i, values in enumerate(date_range_values):

                for metricHeader, value in zip(metric_headers,
                                               values.get('values')):

                    # Append metrics to output row
                    row_d[metricHeader.get('name')] = int(value)

            # Append row of data to output
            data.append(row_d)

    return pandas.DataFrame(data)
