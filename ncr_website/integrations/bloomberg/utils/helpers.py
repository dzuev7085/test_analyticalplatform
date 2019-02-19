"""Helper functions for the Bloomberg integration."""
import os
from datetime import datetime

import pandas as pd


def return_outlook(rating_decision_row):
    """Return what the outlook is on the rating. Could also be
    developing of the issuer has been put on watch."""

    if rating_decision_row.decided_lt_outlook == 1:
        outlook = 'POSITIVE'
    elif rating_decision_row.decided_lt_outlook == 2:
        outlook = 'STABLE'
    elif rating_decision_row.decided_lt_outlook == 3:
        outlook = 'NEGATIVE'
    elif rating_decision_row.decided_lt_outlook in [4, 5, 6]:
        outlook = 'DEVELOPING'
    else:
        # This should never occur
        outlook = 'ERROR'

    return outlook


def return_rating_watch(rating_action, rating_decision_row):
    """If the issuer is placed on watch, return what is the
    most likely outcome."""

    # If rating is rating watch, a separate column should be filled with info
    if rating_action == 'rating watch':
        if rating_decision_row.decided_lt_outlook == 4:
            rating_watch = 'uncertain'
        elif rating_decision_row.decided_lt_outlook == 5:
            rating_watch = 'positive'
        elif rating_decision_row.decided_lt_outlook == 6:
            rating_watch = 'negative'
        else:
            rating_watch = 'none'
    else:
        rating_watch = 'none'

    return rating_watch


def return_rating_action(rating_decision_row, prev_rating):
    """Return type of rating decision."""

    # The case here is that it's a new rating that is public that
    # should be published to Bloomberg.
    # It could also be a confidential or private rating that is
    # converted to a public rating. It should then be reported
    # as a new rating. Therefore, when prev_rating is false,
    # we assume it's a new rating.
    if rating_decision_row.decisionattributes.is_new or not prev_rating:
        # Bloomberg requirement:
        # Rating is newly assigned. This is possible when there have been no
        # prior ratings or when rating was previously withdrawn.

        rating_action = 'new'
    elif rating_decision_row.decided_lt == 200:
        # Bloomberg requirement:
        # Previously assigned rating is being withdrawn.

        rating_action = 'withdrawal'
    else:

        if rating_decision_row.decisionattributes.is_watch:
            # Bloomberg requirement:
            # This indicates that the Rating is being placed under review,
            # and to expect a possible rating change in the near future.
            # Once review is complete, a follow-up upgrade,downgrade or
            # affirmed is sent to indicate the results of the review.

            rating_action = 'rating watch'
        elif rating_decision_row.decisionattributes.is_lt_affirmation:
            # Bloomberg requirement:
            # Previously assigned rating is being affermed as retaining
            # the same value. This normally, but not necessarily, occurs
            # after a prior "rating watch"

            rating_action = 'affirmed'
        elif rating_decision_row.decisionattributes.is_lt_downgrade:
            # Bloomberg requirement:
            # Rating is being assigned that is lower than the previously
            # assigned rating. This normally, but not necessarily,
            # occurs after a prior "rating watch"

            rating_action = 'downgrade'
        elif rating_decision_row.decisionattributes.is_lt_upgrade:
            # Bloomberg requirement:
            # Rating is being assigned that is higher than the previously
            # assigned rating.  This normally, but not necessarily,
            # occurs after a prior "rating watch"

            rating_action = 'upgrade'
        else:
            # This should never occur

            rating_action = 'ERROR'

    return rating_action


def bloomberg_file_name():
    """Generate a file name of the Excel file to be sent to Bloomberg."""

    return 'Bloomberg_{}_{}.xlsx'.format(
        os.environ['ENVIRONMENT_MODE'],
        datetime.now().strftime('%Y-%m-%d'))


def save_to_excel(file_name, debug, issuer_data, issue_data):
    """Saves dataframes for issuers and issues into an Excel file,
    formatted according to Bloomberg's requirements."""

    # ISSUER DATA
    # These are the labels expected by Bloomberg for an Issuer
    labels = ['Internal Issuer ID', 'Issuer Name', 'Rating Action',
              'Rating Type', 'Effective Date', 'Rating', 'Watch',
              'LEI']
    df_issuers = pd.DataFrame.from_records(issuer_data, columns=labels)

    # ISSUE DATA
    # These are the labels expected by Bloomberg for an Issuer
    labels = ['Internal Security ID', 'Issuer Name', 'Security Description',
              'Rating Action', 'Rating Type', 'Effective Date', 'Rating',
              'Watch', 'ISIN']
    df_issues = pd.DataFrame.from_records(issue_data, columns=labels)

    writer = pd.ExcelWriter(file_name)

    # Write to worksheet Issuer
    df_issuers.to_excel(writer, 'Issuer', index=False)
    df_issues.to_excel(writer, 'Issues', index=False)
    writer.save()

    # Debug only
    if debug:
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               10):
            print(df_issuers)

        # Debug only
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               10):
            print(df_issues)
