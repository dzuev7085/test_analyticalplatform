# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0008_auto_20181012_1723'),
    ]

    operations = [
        migrations.CreateModel(
            name='QTOriginator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('bic_code', models.CharField(null=True, max_length=11, blank=True)),
                ('internal_code', models.CharField(null=True, max_length=40, blank=True)),
                ('lei', models.CharField(null=True, max_length=20, blank=True)),
                ('originator_name', models.CharField(null=True, max_length=90, blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='qtprecedingpreliminaryrating',
            old_name='preceding_preliminary_rating',
            new_name='preceding_preliminary_rating_flag',
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='complexity_indicator',
            field=models.IntegerField(null=True, choices=[(1, 'S'), (2, 'C')], blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='corporate_issue_classification',
            field=models.IntegerField(choices=[(1, 'BND'), (2, 'CBR'), (3, 'OCB'), (4, 'OTH')], default=1),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='instrument_unique_identifier',
            field=models.CharField(null=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='issue_program_code',
            field=models.CharField(null=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='other_corporate_issues',
            field=models.CharField(null=True, max_length=50, blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='program_deal_issuance_name',
            field=models.CharField(null=True, max_length=140, blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='serie_program_code',
            field=models.CharField(null=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='structured_finance_transaction_type',
            field=models.IntegerField(null=True, choices=[(1, 'S'), (2, 'M')], blank=True),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='tranche_class',
            field=models.CharField(null=True, max_length=10, blank=True),
        ),
        migrations.AddField(
            model_name='qtratingaction',
            name='outlook_trend',
            field=models.IntegerField(null=True, choices=[(1, 'POS'), (2, 'NEG'), (3, 'EVO'), (4, 'STA')], blank=True),
        ),
        migrations.AddField(
            model_name='qtratingaction',
            name='owsd_status',
            field=models.IntegerField(null=True, choices=[(1, 'P'), (2, 'M'), (3, 'R')], blank=True),
        ),
        migrations.AddField(
            model_name='qtratingaction',
            name='watch_review',
            field=models.IntegerField(null=True, choices=[(1, 'POW'), (2, 'NEW'), (3, 'EVW'), (4, 'UNW')], blank=True),
        ),
        migrations.AddField(
            model_name='qtratingaction',
            name='withdrawal_reason_type',
            field=models.IntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='asset_class',
            field=models.IntegerField(null=True, choices=[(1, 'ABS'), (2, 'RMBS'), (3, 'CMBS'), (4, 'CDO'), (5, 'ABCP'), (6, 'OTH)')], blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='debt_classification_code',
            field=models.CharField(null=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='issuer_rating_type_code',
            field=models.CharField(null=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='local_foreign_currency',
            field=models.IntegerField(choices=[(1, 'LC'), (2, 'FC')], default=2),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='other_rating_type',
            field=models.TextField(null=True, max_length=300, blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='other_sub_asset',
            field=models.CharField(null=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='sector',
            field=models.IntegerField(null=True, choices=[(1, 'FI'), (2, 'IN'), (3, 'CO')], blank=True),
        ),
        migrations.AddField(
            model_name='qtratinginfo',
            name='sub_asset',
            field=models.IntegerField(null=True, choices=[(1, 'CCS'), (2, 'ALB'), (3, 'CNS'), (4, 'SME'), (5, 'LES'), (6, 'HEL'), (7, 'PRR'), (8, 'NPR'), (9, 'CFH'), (10, 'SDO'), (11, 'MVO'), (12, 'SIV'), (13, 'ILS'), (14, 'DPC'), (15, 'SCB'), (16, 'OTH')], blank=True),
        ),
        migrations.AddField(
            model_name='qtoriginator',
            name='instrument_info',
            field=models.ForeignKey(to='esma.QTInstrumentInfo', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
