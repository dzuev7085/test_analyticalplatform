import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from a_helper.static_database_table.models.gics import GICSSubIndustry
from issuer.models import Analyst, Issuer, IssuerType


class Command(BaseCommand):

    def handle(self, *args, **options):

        if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'DEV']:

            rm = User.objects.get(username='commercial')
            analyst1 = User.objects.get(username='analyst1')
            analyst2 = User.objects.get(username='analyst2')

            # DnB
            if not Issuer.objects.filter(lei="549300GKFG0RYRRQ1414").exists():
                bank = IssuerType.objects.get(id=2)
                gics = GICSSubIndustry.objects.get(id=106)

                issuer_id = Issuer.objects.create(
                    lei='549300GKFG0RYRRQ1414',
                    relationship_manager=rm,
                    issuer_type=bank,
                    gics_sub_industry=gics,
                    legal_name='DNB Bank ASA')

                Analyst.objects.filter(
                    issuer=issuer_id).update(primary_analyst=analyst1,
                                             secondary_analyst=analyst2)

            # Vasakronan
            if not Issuer.objects.filter(lei="5493007LNZSEWN5KTV42").exists():
                corporate_re = IssuerType.objects.get(id=3)
                gics = GICSSubIndustry.objects.get(id=154)

                issuer_id = Issuer.objects.create(
                    lei='5493007LNZSEWN5KTV42',
                    relationship_manager=rm,
                    issuer_type=corporate_re,
                    gics_sub_industry=gics,
                    legal_name='Vasakronan AB (publ)')

                Analyst.objects.filter(
                    issuer=issuer_id).update(primary_analyst=analyst1,
                                             secondary_analyst=analyst2)

            # Orkla
            if not Issuer.objects.filter(lei="549300PZS8G8RG6RVZ52").exists():
                corporate = IssuerType.objects.get(id=1)
                gics = GICSSubIndustry.objects.get(id=92)

                issuer_id = Issuer.objects.create(
                    lei='549300PZS8G8RG6RVZ52',
                    relationship_manager=rm,
                    issuer_type=corporate,
                    gics_sub_industry=gics,
                    legal_name='Orkla ASA')

                Analyst.objects.filter(
                    issuer=issuer_id).update(primary_analyst=analyst1,
                                             secondary_analyst=analyst2)
