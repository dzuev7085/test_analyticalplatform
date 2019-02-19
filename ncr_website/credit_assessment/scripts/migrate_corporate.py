"""This module loads data in to the credit assessment app from a csv-file.

Unit tests are not required for this file.
"""
import os
import django
import environ
import sys
import pandas as pd
from dateutil import parser
from pygleif import GLEIF
from dateutil import tz
from pycreditrating import (
    Rating as PCRRating,
    RATING_LONG_TERM
)
import traceback

ROOT_DIR = str(environ.Path(__file__) - 3)
sys.path.insert(0, ROOT_DIR)

# SETUP
# ------------------------------------------------------------------------------
# Load .env variables into OS Environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'
django.setup()

from issuer.models import Issuer  # noqa: E402
from credit_assessment.models.assessment import AssessmentJob  # noqa: E402
from credit_assessment.models.subscores import (  # noqa: E402
    AssessmentSubscoreData
)
from credit_assessment.models.seniority_level_assessment import (  # noqa: E40
    SeniorityLevelAssessment
)
from rating_process.util import (  # noqa: E402
    generate_rating_dict
)
from a_helper.static_database_table.models.gics import (  # noqa: E402
    GICSSubIndustry
)
from issuer.models.classification import Classification  # noqa: E402
from credit_assessment.models.highest_lowest import HighestLowest  # noqa: E402


df = pd.read_csv('data.csv',
                 sep=';')

df['comment'] = df['comment'].astype(str)
df['ncr_peer'] = df['ncr_peer'].astype(str)
df['date_time_creation'] = df['date_time_creation'].astype(str)


try:
    df['secured'] = df['secured'].astype(str)
except KeyError:
    pass


try:
    df['senior_unsecured'] = df['senior_unsecured'].astype(str)
except KeyError:
    pass

try:
    df['subordinated'] = df['subordinated'].astype(str)
except KeyError:
    pass

try:
    df['senior_npf'] = df['senior_npf'].astype(str)
except KeyError:
    pass

try:
    df['tier2'] = df['tier2'].astype(str)
except KeyError:
    pass

try:
    df['at1'] = df['at1'].astype(str)
except KeyError:
    pass


df['is_current'] = df['is_current'].fillna(False).astype(bool)

df['is_aaa'] = df['is_aaa'].fillna(False).astype(bool)
df['is_aa_plus'] = df['is_aa_plus'].fillna(False).astype(bool)
df['is_ccc'] = df['is_ccc'].fillna(False).astype(bool)
df['is_cc'] = df['is_cc'].fillna(False).astype(bool)
df['is_c'] = df['is_c'].fillna(False).astype(bool)


for index, row in df.iterrows():

    assessment = False
    previous_assessment = None
    i = None

    lei = row['lei']

    is_current = row['is_current']

    initiated_by = int(row['initiated_by_id'])

    issuer_type_id = int(row['issuer_type_id'])

    # Check to see if there is a previous assessment id
    if not pd.isnull(row['previous_assessment_id']):
        previous_assessment = int(row['previous_assessment_id'])

    date_time_creation = parser.parse(row['date_time_creation'])
    date_time_creation = date_time_creation.replace(tzinfo=tz.tzutc())
    date_time_approval = date_time_creation

    ncr_peer = str(row['ncr_peer'])

    is_aaa = row['is_aaa']
    is_aa_plus = row['is_aa_plus']
    is_ccc = row['is_ccc']
    is_cc = row['is_cc']
    is_c = row['is_c']

    # Insert issuer if it does not exist
    try:

        i = Issuer.objects.get(
            lei=lei,
        )

    except Issuer.DoesNotExist:

        try:

            try:
                gleif_data = GLEIF(lei)

                legal_name = gleif_data.entity.legal_name

            except Exception:

                legal_name = lei

            i = Issuer.objects.create(
                lei=lei,
                issuer_type_id=issuer_type_id,
                legal_name=legal_name,
                short_name=legal_name,
                gics_sub_industry_id=None,
            )

        except Exception as e:
            print('Could not insert LEI {} due to {}'.format(
                lei,
                e
            ))

    # Set the correct GICS dode
    try:
        gics = GICSSubIndustry.objects.get(
            code=row['gics_code']
        )

    except Exception:

        gics = None

    try:
        i.gics_sub_industry = gics
        i.save()
    except AttributeError:
        pass

    if len(ncr_peer) > 5:

        Classification.objects.filter(issuer=i).update(peer_free_text=ncr_peer)
    else:
        Classification.objects.filter(issuer=i).update(peer_free_text=None)

    # Create an assessment if it does not exist
    try:

        assessment = AssessmentJob.objects.get(
            issuer=i,
        )

        assessment.date_time_approval = date_time_approval
        assessment.date_time_creation = date_time_creation
        assessment.save()

    except AssessmentJob.DoesNotExist:

        try:
            assessment = AssessmentJob.objects.create(
                issuer=i,
                initiated_by_id=initiated_by,
                approved_by_id=initiated_by,
                process_step=10,
                date_time_creation=date_time_creation,
                date_time_approval=date_time_approval,
            )

        except Exception as e:
            print(e)

    try:
        if not pd.isnull(row['comment']):

            if str(row['comment']) != 'nan':
                assessment.comment = str(row['comment'])
                assessment.save()

    except AttributeError as e:

        print(e)

    print(assessment)

    try:
        assessment.previous_assessment_id = previous_assessment
        assessment.is_current = is_current
        assessment.save()
    except AttributeError as e:

        print(e)

    # Highest and lowest ratings
    HighestLowest.objects.filter(assessment=assessment).update(is_aaa=is_aaa)
    HighestLowest.objects.filter(assessment=assessment).update(
        is_aa_plus=is_aa_plus)
    HighestLowest.objects.filter(assessment=assessment).update(is_ccc=is_ccc)
    HighestLowest.objects.filter(assessment=assessment).update(is_cc=is_cc)
    HighestLowest.objects.filter(assessment=assessment).update(is_c=is_c)

    for column in df:

        if df[column].name[0:2] == 'w_':
            df[df[column].name] = df[df[column].name].fillna(False).astype(
                float)

        if df[column].name in ['secured', 'senior_unsecured', 'subordinated',
                               'senior_npf', 'tier2', 'at1']:

            if df[column].name == 'secured':
                s_id = 2
            elif df[column].name == 'senior_unsecured':
                s_id = 1
            elif df[column].name == 'subordinated':
                s_id = 4
            elif df[column].name == 'senior_npf':
                s_id = 5
            elif df[column].name == 'tier2':
                s_id = 4
            elif df[column].name == 'at1':
                s_id = 3

            a_value = str(row[df[column].name])

            if a_value != 'nan':
                try:
                    i_data = SeniorityLevelAssessment.objects.get(
                        assessment=assessment,
                        seniority_id=s_id
                    )

                except SeniorityLevelAssessment.DoesNotExist:
                    pass

                try:
                    i_data.decided_lt = RATING_LONG_TERM[
                        a_value.upper()]
                    i_data.save()
                except Exception as e:
                    print(e)

        try:

            d = None

            if df[column].name[0:2] != 'w_' and \
                    df[column].name not in ['issuer', 'sheet_name', 'lei',
                                            'id', 'previous_assessment_id',
                                            'issuer_type_id', 'is_current',
                                            'initiated_by_id', 'process_step',
                                            'date_time_creation', 'comment',
                                            'senior_unsecured', 'senior_npf',
                                            'tier2', 'at1', 'ncr_peer',
                                            'is_aaa', 'is_aa_plus', 'is_ccc',
                                            'is_cc', 'is_c']:

                d = AssessmentSubscoreData.objects.get(
                    assessment=assessment,
                    subfactor__name=df[column].name,
                )

                if df[column].name in ['Liquidity',
                                       'Peer comparison',
                                       'ESG',
                                       'Ownership support',
                                       'Transitions',
                                       'Borderline assessments',
                                       'Material credit enhancement',
                                       'Rating caps']:

                    d.decided_notch_adjustment = int(row[df[column].name])
                else:

                    if df[column].name[0:2] != 'w_':

                        score = row[df[column].name]
                        if str(score) != 'nan' and int(score) > 0:
                            w = row['w_' + df[column].name]
                            if str(w) == 'nan':
                                d.weight = None
                                d.decided_score = None
                            else:
                                d.decided_score = score
                                d.weight = w

                        else:
                            d.weight = None
                            d.decided_score = None

                d.save()

        except Exception as err:
            traceback.print_tb(err.__traceback__)

# Set assessment per assessment job
for a in AssessmentJob.objects.all():

    internal_score_obj = AssessmentSubscoreData.objects.filter(
        assessment_id=a.id
    ).all()

    # Issuer type id is used to create the rating below
    issuer_type_id = a.issuer.issuer_type.id

    try:
        # Return indicative ratings based on score input
        rating_dict = generate_rating_dict(
            issuer_type_id,
            internal_score_obj,
            'decided',
            version=2)

        proposed_rating = PCRRating(rating_dict)

        c_assessment = RATING_LONG_TERM[
            proposed_rating.issuer_rating.upper()]

    except Exception as e:
        print('{} due to {}'.format(a, e))

        from pprint import pprint
        pprint(rating_dict)

        c_assessment = None

    try:
        # Assign and save the assessment
        a.assessment_lt = c_assessment
        a.save()

    except AttributeError as e:
        print("Did not save {} due to {}".format(
            a,
            e
        ))
