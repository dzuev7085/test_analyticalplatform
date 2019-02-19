"""Setup users in PROD and UAT environments. This is a good enough solution
until we sync against Intillity's AD."""
import os

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

from user_profile.models import Profile, LeadAnalyst

from a_helper.static_database_table.models.country import CountryRegion


def create_user(username,
                email,
                first_name,
                last_name,
                groups,
                title,
                number,
                country,
                attributes):
    """Create a user."""

    if not User.objects.filter(username=username).exists():

        # Create a new user
        user_id = User.objects.create(
            username=username,
            email=email,
            password="!",
            first_name=first_name,
            last_name=last_name)

        # Manually set the password to
        # something simple that can be changed later
        # by the user
        user_id.set_password('abc123')
        user_id.save()

    user_id = User.objects.get(username=username)
    office_location = CountryRegion.objects.get(
        iso_31661_alpha_2=country)

    # user_set adds a person to a group
    for group in groups:
        user_id.groups.add(group)

    Profile.objects.filter(
        pk=user_id.id).update(title=title,
                              phone_number=number,
                              office_location=office_location)

    # Add a record to the lead analyst table if a record does not exist
    if attributes['lead_analyst']['has_attribute']:
        if not LeadAnalyst.objects.filter(profile=user_id.profile).exists():
            LeadAnalyst.objects.create(
                profile=user_id.profile,
                start_date=attributes['lead_analyst']['start_date']
            )


class Command(BaseCommand):

    def handle(self, *args, **options):

        if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'PROD', 'DEV']:

            commercial = Group.objects.get(name='Commercial')
            analyst = Group.objects.get(name='Analyst')
            editor = Group.objects.get(name='Editor')
            review = Group.objects.get(name='Review')
            compliance = Group.objects.get(name='Compliance')
            senior_analyst = Group.objects.get(name='Senior level analyst')
            cro = Group.objects.get(name='Chief rating officer')

            create_user(
                username="sg01",
                email="gustav.liedgren@nordiccreditrating.com",
                first_name="Gustav",
                last_name="Liedgren",
                groups=[commercial],
                title='CEO',
                number='+46736496543',
                country='SE',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
                    }
                },
            )

            create_user(
                username="sg02",
                email="michael.andersson@nordiccreditrating.com",
                first_name="Michael",
                last_name="Andersson",
                groups=[analyst,
                        senior_analyst,
                        cro],
                title='Chief Rating Officer',
                number='+46707635069',
                country='SE',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-02'
                    }
                },
            )

            create_user(
                username="sg03",
                email="jan.pollestad@nordiccreditrating.com",
                first_name="Jan",
                last_name="Pollestad",
                groups=[commercial],
                title='Commercial Business Manager',
                number='+4791713823',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
                    }
                },
            )

            create_user(
                username="sg04",
                email="sean.cotten@nordiccreditrating.com",
                first_name="Sean",
                last_name="Cotten",
                groups=[analyst,
                        senior_analyst],
                title='Lead Analyst',
                number='+46735600337',
                country='SE',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-01-19'
                    }
                },
            )

            create_user(
                username="sg05",
                email="carl.olsson@nordiccreditrating.com",
                first_name="Carl",
                last_name="Olsson",
                groups=[compliance],
                title='Chief Compliance Officer',
                number='+4740346009',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
                    }
                },
            )

            create_user(
                username="sg06",
                email="patrik.lindgren@nordiccreditrating.com",
                first_name="Patrik",
                last_name="Lindgren",
                groups=[analyst],
                title='Analyst',
                number='+46708627772',
                country='SE',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-04-23'
                    }
                },
            )

            create_user(
                username="sg07",
                email="geir.kristiansen@nordiccreditrating.com",
                first_name="Geir",
                last_name="Kristiansen",
                groups=[analyst],
                title='Credit Rating Analyst',
                number='+4790784593',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-08-01'
                    }
                },
            )

            create_user(
                username="sg08",
                email="mille.fjeldstad@nordiccreditrating.com",
                first_name="Mille",
                last_name="O. Fjeldstad",
                groups=[analyst],
                title='Credit Rating Analyst',
                number='+4799038916',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': True,
                        'start_date': '2018-05-01'
                    }
                },
            )

            create_user(
                username="sg09",
                email="petter.e.delange@nordiccreditrating.com",
                first_name="Petter",
                last_name="Eilif De Lange",
                groups=[review],
                title='Review Function',
                number='+4797720887',
                country='NO',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
                    }
                },
            )

            create_user(
                username="ex01",
                email="oliver@hilltop-lang.co.uk",
                first_name="Oliver",
                last_name="Dirs",
                groups=[editor],
                title='Editor',
                number='+447565300180',
                country='GB',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
                    }
                },
            )

            create_user(
                username="ex02",
                email="stafford.mawhinney@gmail.com",
                first_name="Stafford",
                last_name="Mawhinney",
                groups=[editor],
                title='Editor',
                number='',
                country='GB',
                attributes={
                    'lead_analyst': {
                        'has_attribute': False
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
