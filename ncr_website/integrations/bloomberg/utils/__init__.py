"""Util functions for sending data to Bloomberg."""
import datetime as dt
import os
from datetime import timedelta

from a_helper.other.tasks import delete_files_task
from gui.templatetags.template_tags import previous_rating
from integrations.bloomberg.utils.helpers import (
    return_outlook,
    return_rating_watch,
    return_rating_action,
    bloomberg_file_name,
    save_to_excel
)
from issue.models import Issue
from rating_process.models.rating_decision import RatingDecision
from rating_process.models.rating_decision_issue import RatingDecisionIssue

# List to store data in
ISSUER_DATA = []
ISSUE_DATA = []


def issue_rows(rating_decision_row, issue_decision_row, issue_row):
    """Convert a rating decision for an issue to the format required by
    Bloomberg"""

    """Requirement:
    1	Field header: Internal Security ID
        Type: Internal ID
        Description: Identifier assigned by agency to uniquely identify a
        secuirty
        Identification of correct values: See Internal ID tab for rules
        determining valid values

    2	Issuer Name
        String
        Name of issuer
        Length between 1 and 120 characters, can not include pipe character

    3	Security Description
        String
        Descriptive string identifying the security
        Length between 1 and  80 characters, can not include pipe character

    4	Rating Action
        Rating Action
        Action that row in feed file indicates is happening
        See Issuer Rating Action tab for valid values and descriptions

    5	Rating Type
        Issuer Rating Type
        Type of rating associated with rating action
        See Issuer Rating Type tab for valid values and descriptions

    6	Effective Date
        date
        Effective date of rating action
        Dates will be provided in YYYY-MM-DD format, and should represent
        dates before or on the current date and after the start of rating
        coverage.

    7	Rating
        Dependent on Rating Type
        See Rating Scales Tab to determine valid values

    8	Watch
        Watch Type
        Indication if rating is being reviewed for change
        See Rating Watch tab to determine valid values

    9	ISIN
        ISIN
        ISIN identifier of issue (NOT Issuer)
        Valid ISIN or blank
    """

    row_1 = {}

    row_1.update({'Internal Security ID': issue_row.id})

    # Issuer name
    issuer_name = rating_decision_row.issuer.legal_name
    row_1.update({'Issuer Name': issuer_name})

    # Security description
    security_description = issue_row.name
    row_1.update({'Security Description': security_description})

    # Used in the code to determined if this is an
    # upgrade/downgrade or affirmation
    prev_rating = previous_rating(rating_decision_row.issuer,
                                  is_bloomberg=True)

    # Determine type of rating action
    rating_action = return_rating_action(rating_decision_row, prev_rating)

    row_1.update({'Rating Action': rating_action})

    row_1.update({'Rating Type': 'Long Term Issue Credit Rating'})

    # The publishing date is considered as the effective date
    effective_date = issue_decision_row.rating_decision.date_time_published. \
        strftime('%Y-%m-%d')
    row_1.update({'Effective Date': effective_date})

    # The long-term issue rating
    # Append P if preliminary rating
    if rating_decision_row.is_preliminary:
        lt = '(P) ' + issue_decision_row.get_decided_lt_display()
    else:
        lt = issue_decision_row.get_decided_lt_display()

    row_1.update({'Rating': lt})

    # If rating is rating watch, a separate column should be filled with info
    rating_watch = return_rating_watch(rating_action, rating_decision_row)
    row_1.update({'Watch': rating_watch})

    # Isin number
    isin = issue_row.isin
    row_1.update({'ISIN': isin})

    ISSUE_DATA.append(row_1)


def issuer_rows(rating_decision_row):
    """Expand a rating decision to the format required by Bloomberg."""

    # NRC's unique issuer id number
    issuer_id = rating_decision_row.issuer.id

    # Used in the code to determined if this is an
    # upgrade/downgrade or affirmation
    prev_rating = previous_rating(rating_decision_row.issuer,
                                  is_bloomberg=True)

    # The name of the issuer
    # Based on GLEIF data
    issuer_name = rating_decision_row.issuer.legal_name
    lei_code = rating_decision_row.issuer.lei

    # The publishing date is considered as the effective date
    effective_date = rating_decision_row.date_time_published.strftime(
        '%Y-%m-%d')

    # The long-term issuer rating
    lt = rating_decision_row.get_decided_lt_display()

    # Bloomberg uses the same scale, but with an S instead of N
    st = rating_decision_row.get_decided_st_display().replace('N', 'S')

    # Determine type of rating action
    rating_action = return_rating_action(rating_decision_row, prev_rating)

    # If rating is rating watch, a separate column should be filled with info
    rating_watch = return_rating_watch(rating_action, rating_decision_row)

    # Determine outlook of the issuer
    outlook = return_outlook(rating_decision_row)

    # If this is a withdrawal of the rating, Bloomberg expects a WR in
    # all columns
    if rating_action == 'withdrawal':
        outlook = 'WR'
        lt = 'WR'
        st = 'WR'

    row_1 = {}
    row_2 = {}
    row_3 = {}

    row_1.update({'Rating Type': 'Long Term Issuer Credit Rating'})
    row_2.update({'Rating Type': 'Outlook'})
    row_3.update({'Rating Type': 'Short Term Issuer Credit Rating'})

    row_1.update({'Rating': lt})
    row_2.update({'Rating': outlook})
    row_3.update({'Rating': st})

    row_1.update({'Rating Action': rating_action})
    row_2.update({'Rating Action': rating_action})
    row_3.update({'Rating Action': rating_action})

    row_1.update({'Internal Issuer ID': issuer_id})
    row_2.update({'Internal Issuer ID': issuer_id})
    row_3.update({'Internal Issuer ID': issuer_id})

    row_1.update({'Issuer Name': issuer_name})
    row_2.update({'Issuer Name': issuer_name})
    row_3.update({'Issuer Name': issuer_name})

    row_1.update({'Effective Date': effective_date})
    row_2.update({'Effective Date': effective_date})
    row_3.update({'Effective Date': effective_date})

    row_1.update({'LEI': lei_code})
    row_2.update({'LEI': lei_code})
    row_3.update({'LEI': lei_code})

    row_1.update({'Watch': rating_watch})
    row_2.update({'Watch': rating_watch})
    row_3.update({'Watch': rating_watch})

    ISSUER_DATA.append(row_1)
    ISSUER_DATA.append(row_2)
    ISSUER_DATA.append(row_3)


def run_script(debug=False):
    """Create data to be sent to Bloomberg."""

    file_name = bloomberg_file_name()

    """Loop through today's decisions."""
    for rating_decision in RatingDecision.objects.bloomberg():

        issuer_rows(rating_decision)

        # Loop through each issue seniority level that was part
        # of the decision
        for issue_decision in RatingDecisionIssue.objects.filter(
                rating_decision=rating_decision):

            # Loop through each issue with the given seniority level.
            for issue in Issue.objects.filter(
                issuer=rating_decision.issuer,
                    seniority=issue_decision.seniority):
                issue_rows(rating_decision, issue_decision, issue)

    # Only save file and return a non-False value if there are
    # ratings issued today
    if len(ISSUER_DATA) > 0 or len(ISSUE_DATA) > 0:

        # Save the data in Excel format
        save_to_excel(
            file_name,
            debug,
            ISSUER_DATA,
            ISSUE_DATA
        )

        # Create a task to delete the Excel file
        # Set the time in the future so to avoid a race
        # condition when mailing the file
        later = dt.datetime.utcnow() + timedelta(minutes=10)
        files = [
            os.path.abspath(file_name),
        ]
        delete_files_task.apply_async(files, eta=later)

        return file_name

    else:

        return False
