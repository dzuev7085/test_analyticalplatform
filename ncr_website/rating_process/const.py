# flake8: noqa
PHASES_HUMAN_READABLE = {
    'setup': 'Rating job setup',
    'pre_committee': 'Pre committee',
    'analytical_phase': 'Analytical phase',
    'post_committee': 'Post committee',
    'editor_phase': 'Editing',
    'issuer_confirmation_phase': 'Issuer confirmation',
    'analyst_final_approval_phase': 'Analyst final approval',
    'chair_final_approval_phase': 'Chair final approval',
    'publishing_phase': 'Ready for publishing',
    'surveillance': 'Ongoing surveillance',
    'not_started': 'Initial rating not started',
}

PROCESS_STEPS = (
    (1, 'setup'),
    (2, 'pre_committee'),
    (3, 'analytical_phase'),
    (4, 'post_committee'),
    (5, 'editor_phase'),
    (6, 'issuer_confirmation_phase'),
    (7, 'analyst_final_approval_phase'),
    (8, 'chair_final_approval_phase'),
    (9, 'publishing_phase'),
    (10, 'publishing_phase_done'),
)

SETUP_HEADER = '{} | A chair has been appointed for rating job {}'
SETUP_BODY = """Dear %s,
<p>
Please log in into the analytical platform to finalize the pre-committee stage."""

PRE_COMMITTEE_HEADER = "{} | {} has started the analytical phase for rating job {}"
PRE_COMMITTEE_BODY = """Dear %s,
<p>
Please log in into the analytical platform to finalize the analytical phase.."""

ISSUER_HEADER = "Notification of draft report"

ISSUER_EMAIL = """Dear client,
<p>
Please find attached the draft rating report. You are welcome to comment on any factual errors or inadvertent inclusion of confidential information which we will take into account and amend accordingly. We will not amend any of our analytical opinions or conclusions which are the outcome of our analytical and committee process. Please revert to us within 24 hours (of which eight are within business hours). After 24 hours have elapsed we can release the report regardless of your response. Please return to the primary analyst (copied herein) with any questions you might have.
<p>
A password to open the file will be sent in a separate email.
<p>
Best regards,<br>
%s
<p>
<p>
**Disclaimer**<br>
The information included in this e-mail, including any attachments, is strictly confidential and may not be distributed to any unauthorized persons. The information provided relating to the credit ratings activities by Nordic Credit Ratings may constitute inside information as defined in the Market Abuse Regulation (EU) No 596/2014 ("MAR"). If the relevant financial instruments (i) are admitted to trading on a trading venue (regulated market, multilateral trading facility or organized trading facility) in the EEA, (ii) for which a request for admission has been made to trading on a trading venue or (iii) traded over the counter and either depend on or have an effect on the price or value of a financial instrument referred to in (i) or (ii) above. The company who receives the inside information shall provide all names of the persons who have been given access to the information in the company to Nordic Credit Rating if requested by NCR. A failure to comply with the obligations in MAR may be sanctioned by the relevant competent authority. The company has an independent obligation to comply with MAR, including an obligation to manage their own internal insider lists in accordance with MAR, to the extent applicable."""

ISSUER_EMAIL_HEADER_PASSWORD = "Password to draft report"

ISSUER_EMAIL_BODY_PASSWORD = """Dear client,
<p>
The password to open the file {} is {}.
<p>
Best regards,<br>
{}"""


EDITOR_HEADER = "{} | an editing task has been assigned to you for rating job {}"

EDITOR_EMAIL = """Dear %s,
<p>
This is to let you know that we have uploaded a document to the editing process Sharepoint windows folder.
<p>
Kind regards,<br>
%s"""


ANALYTICAL_PHASE_HEADER = "{} | the committee pack has been submitted to the rating committee on {} for rating job {}"
ANALYTICAL_PHASE_BODY = """Dear all,
<p>
Please log in into the analytical platform to download the committee package."""

ANALYST_FINAL_APPROVAL_HEADER = "{} | the rating job has been assigned to you for final approval"
ANALYST_FINAL_APPROVAL_BODY = """Dear %s,
<p>
Please log in into the analytical platform to give your final approval of the rating job.
"""

CHAIR_FINAL_APPROVAL_HEADER = "{} | the rating job is ready to published"
CHAIR_FINAL_APPROVAL_BODY = """Dear %s,
<p>
Please log in into the analytical platform and finalize storing the rating in the database.
"""


MEMBER_ADDED_HEADER = "Credit Rating Committee for %s"
MEMBER_ADDED_BODY = """Dear %s,

You have been suggested by %s to sit in as %s in the credit rating committee for %s.

Log into the analytical platform to confirm taking part of the committee.
"""

ENGAGEMENT_LETTER_HEADER = "An engagement letter has been signed for %s"
ENGAGEMENT_LETTER_BODY = """Hi,
<p>
An engagement letter has been signed. Please log into the analytical platform to finalize the onboarding process."""

ISSUE_DECISION_HEADER = 'Rating decision regarding issue with ISIN {}'
ISSUE_DECISION_BODY = """Dear client,
<br><br>
This is to inform you that we have assigned the rating '{}' to the
issue with ISIN {}.
<br><br>
Please contact the primary analyst copied herein if you have any 
questions. Also note that you can not reply directly to this email address.

Best regards,
Nordic Credit Rating
"""

ISSUE_WR_DECISION_HEADER = "Rating decision regarding issue with ISIN {}"
ISSUE_WR_DECISION_BODY = """Dear client,
<br><br>
This is to inform you that we have withdrawn the rating on the
issue with ISIN {} due to the bond having matured.
<br><br>
Please contact the primary analyst copied herein if you have any 
questions. Also note that you can not reply directly to this email address.

Best regards,
Nordic Credit Rating"""
