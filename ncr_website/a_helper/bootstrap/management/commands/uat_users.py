"""Create a set of test users in dev and UAT environments.
Note that the passwords must be reset due to Django restrictions."""
import os

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from .prod_users import create_user


class Command(BaseCommand):

    def handle(self, *args, **options):
        if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'DEV']:

            analyst = Group.objects.get(name='Analyst')
            commercial = Group.objects.get(name='Commercial')
            editor = Group.objects.get(name='Editor')
            review = Group.objects.get(name='Review')
            compliance = Group.objects.get(name='Compliance')
            senior_analyst = Group.objects.get(name='Senior level analyst')
            cro = Group.objects.get(name='Chief rating officer')

            create_user(
                username="analyst1",
                email="analyst1@host.com",
                first_name="Analytical",
                last_name="Personone",
                groups=[analyst],
                title='Analyst',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="analyst2",
                email="analyst2@host.com",
                first_name="Analytical",
                last_name="Persontwo",
                groups=[analyst],
                title='Analyst',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="senioranalyst1",
                email="senioranalyst1@host.com",
                first_name="Señor",
                last_name="Analystone",
                groups=[senior_analyst],
                title='Senior analyst',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="senioranalyst2",
                email="senioranalyst2@host.com",
                first_name="Señor",
                last_name="Analysttwo",
                groups=[senior_analyst],
                title='Senior analyst',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="senioranalyst3",
                email="senioranalyst3@host.com",
                first_name="Señor",
                last_name="Analystthree",
                groups=[senior_analyst],
                title='Senior analyst',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="commercial",
                email="commercial@host.com",
                first_name="Commercial",
                last_name="Personone",
                groups=[commercial],
                title='Commercial manager',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False,
                    }
                },
            )

            create_user(
                username="editor",
                email="editor@host.com",
                first_name="Editor",
                last_name="Personone",
                groups=[editor],
                title='Editor Specialist',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False,
                    }
                },
            )

            create_user(
                username="review",
                email="review@host.com",
                first_name="Review",
                last_name="Personone",
                groups=[review],
                title='Review Specialist',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False,
                    }
                },
            )

            create_user(
                username="compliance",
                email="compliance@host.com",
                first_name="Compliance",
                last_name="Personone",
                groups=[compliance],
                title='Compliance Officer',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False,
                    }
                },
            )

            create_user(
                username="cro",
                email="cro@host.com",
                first_name="CRO",
                last_name="Personone",
                groups=[cro],
                title='Chief Rating Officer',
                number='+46708000000',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="tron",
                email="production@nordiccreditrating.com",
                first_name="System",
                last_name="User",
                groups=[],
                title='System Account',
                number='',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
                    }
                },
            )
