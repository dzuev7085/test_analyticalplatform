import pandas as pd
import datetime
from django.conf import settings as djangoSettings
import uuid
from a_helper.other.tasks import delete_files_task
import os
from datetime import timedelta
from a_helper.static_database_table.models.country import CountryRegion
from integrations.google.analytics.utils.queries import (
    UNIQUE_PAGEVIEWS,
    UNIQUE_EVENTS,
    TOTAL_USERS,
)
from integrations.google.utils.connect import (
    return_response,
    get_service,
)


# The column names of the output dataframe
COLUMN_NAMES = ['city', 'country', 'country_iso_code', 'date_int', 'path',
                'region', 'value', 'type']


def get_users(s):
    """Get data for pageviews.
    :param: (Object) profile: A profile object.
    :returns: (pandas Dataframe) Dataframe containing pageview data.
    """

    df = return_response(s, TOTAL_USERS)
    df['type'] = 'users'
    df.columns = COLUMN_NAMES

    return df


def get_unique_pageviews(s):
    """Get data for users.
    :param: (Object) profile: A profile object.
    :returns: (pandas Dataframe) Dataframe containing users data.
    """

    df = return_response(s, UNIQUE_PAGEVIEWS)
    df['type'] = 'unique_pageviews'
    df.columns = COLUMN_NAMES

    return df


def get_total_events(s):
    """Get data for events.
    :param: (Object) profile: A profile object.
    :returns: (pandas Dataframe) Dataframe containing events data.
    """

    df = return_response(s, UNIQUE_EVENTS)
    df['type'] = 'events'
    df.columns = COLUMN_NAMES

    # Lowercase for filtering
    df['path'] = df['path'].astype(str).str.lower()

    # Only include files that are in the upload category
    df = df[df.path.str.startswith('/uploads')]

    return df


def create_csv(issuer_obj):
    """Create a CSV-file for the Google Analytics Data.
    :returns: (pandas Dataframe) Dataframe containing all data from Google
        Analytics.
    """

    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = str(djangoSettings.ROOT_DIR + '.google_auth.json')

    s = get_service(
        api_name='analytics',
        api_version='v4',
        scopes=[scope],
        key_file_location=key_file_location)

    df_list = []

    # Page views
    df_list.append(get_users(s))

    # Events
    df_list.append(get_total_events(s))

    # Users
    df_list.append(get_unique_pageviews(s))

    relevant_data = pd.concat(
        df_list,
        sort=False,
    )

    # Make the date column into the index
    relevant_data['date'] = pd.to_datetime(relevant_data['date_int'])
    relevant_data = relevant_data.set_index('date')

    # Drop the int representation of the date
    relevant_data = relevant_data.drop(columns=['date_int'])

    # Replace country code with ISO-3
    country = dict(CountryRegion.objects.all().values_list(
        'iso_31661_alpha_2',
        'iso_31661_alpha_3'
    ))

    # Replace ISO-2 with ISO-3
    relevant_data['country_iso_code'] = relevant_data[
        'country_iso_code'].map(country)

    # Lowercase for filtering later on
    relevant_data['path'] = relevant_data['path'].astype(str).str.lower()

    # Filter out 404: page not found
    relevant_data = relevant_data[
        ~relevant_data.path.str.contains('404')]

    # TODO: make more generic
    if issuer_obj.id == 1:
        issuer_filter_name = 'vacse'
    elif issuer_obj.id == 2:
        issuer_filter_name = 'malardalen'
    elif issuer_obj.id == 3:
        issuer_filter_name = 'rekarne'
    elif issuer_obj.id == 4:
        issuer_filter_name = 'akershus'

    # Filter only pages containing issuer name
    relevant_data = relevant_data[
        relevant_data.path.str.contains(issuer_filter_name)]

    # Create file name for CSV file
    file_name = '{}.csv'.format(
        uuid.uuid4())

    # Save Dataframe as CSV
    relevant_data.to_csv(
        file_name,
        sep='\t',
        encoding='utf-8',
        index=True
    )

    # Delete the temporary file
    # Do it in the future to avoid race condition
    later = datetime.datetime.utcnow() + timedelta(seconds=20)
    files = [
        os.path.abspath(file_name)
    ]
    delete_files_task.apply_async(files, eta=later)

    return relevant_data
