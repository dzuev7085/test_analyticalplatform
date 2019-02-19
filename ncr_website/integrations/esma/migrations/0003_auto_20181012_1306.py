# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0002_pressrelease'),
        ('static_database_table', '0002_crainfo'),
        ('upload', '0001_initial'),
        ('issue', '0001_initial'),
        ('esma', '0002_auto_20181011_1312'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionDateInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('validity_date', models.DateTimeField()),
                ('communication_date', models.DateTimeField()),
                ('decision_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='AttachedDocument',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('type', models.IntegerField(choices=[(1, 'P'), (2, 'R')])),
                ('language', models.CharField(max_length=2)),
                ('document', models.ForeignKey(to='upload.AnalyticalDocument', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('isin_code', models.CharField(blank=True, null=True, max_length=12)),
                ('issuance_date', models.DateField(blank=True, null=True)),
                ('maturity_date', models.DateField(blank=True, null=True)),
                ('outstanding_issue_volume', models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=13)),
                ('currency', models.ForeignKey(blank=True, null=True, to='static_database_table.Currency', on_delete=django.db.models.deletion.PROTECT)),
                ('issue', models.ForeignKey(to='issue.Issue', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='IssuerInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('lei_code', models.CharField(max_length=20)),
                ('issuer_name', models.CharField(max_length=90)),
            ],
        ),
        migrations.CreateModel(
            name='LeadAnalystInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('lead_analyst_code', models.CharField(max_length=40)),
                ('CountryRegion_model', models.ForeignKey(to='static_database_table.CountryRegion', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='PrecedingPreliminaryRating',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('preceding_preliminary_rating', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='RatingAction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('action_type', models.IntegerField(choices=[(1, 'OR'), (2, 'PR'), (3, 'NW'), (4, 'UP'), (5, 'DG'), (6, 'AF'), (7, 'DF'), (8, 'SP'), (9, 'WD'), (10, 'OT'), (11, 'WR')])),
            ],
        ),
        migrations.CreateModel(
            name='RatingActionInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('rating_issuance_location', models.IntegerField(choices=[(1, 'I'), (2, 'E'), (3, 'T'), (4, 'O'), (5, 'N')])),
                ('rating_solicited_unsolicited', models.IntegerField(choices=[(1, 'S'), (2, 'U'), (3, 'P'), (4, 'N')])),
                ('press_release_flag', models.BooleanField(default=False)),
                ('research_report_flag', models.BooleanField(default=False)),
                ('press_release', models.ForeignKey(blank=True, related_name='document_press_release', null=True, to='esma.AttachedDocument', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='RatingCreateData',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('reporting_type', models.IntegerField(choices=[(1, 'NEW')])),
                ('rating_identifier', models.IntegerField()),
                ('rating_decision', models.ForeignKey(to='rating_process.RatingDecision', on_delete=django.db.models.deletion.PROTECT)),
                ('xml_file', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, null=True, to='esma.XMLFile')),
            ],
        ),
        migrations.CreateModel(
            name='RatingInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('responsible_cra_lei', models.CharField(max_length=20)),
                ('issuer_cra_lei', models.CharField(max_length=20)),
                ('rating_type', models.IntegerField(choices=[(1, 'C'), (2, 'S'), (3, 'T'), (4, 'O')])),
                ('rated_object', models.IntegerField(choices=[(1, 'ISR'), (2, 'INT')])),
                ('time_horizon', models.IntegerField(choices=[(1, 'L'), (2, 'S')])),
                ('industry', models.IntegerField(choices=[(1, 'FI'), (2, 'IN'), (3, 'CO')])),
                ('type_of_rating_for_erp', models.IntegerField(choices=[(1, 'NXI'), (2, 'EXI')], default=2)),
                ('relevant_for_cerep', models.BooleanField(default=False)),
                ('CountryRegion_model', models.ForeignKey(to='static_database_table.CountryRegion', on_delete=django.db.models.deletion.PROTECT)),
                ('rating_action', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingAction')),
            ],
        ),
        migrations.CreateModel(
            name='RatingValue',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('rating_value', models.IntegerField()),
                ('default_flag', models.BooleanField(default=False)),
                ('rating_action', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingAction')),
                ('rating_scale', models.ForeignKey(to='static_database_table.RatingScale', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='ratingactioninfo',
            name='rating_create_data',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingCreateData'),
        ),
        migrations.AddField(
            model_name='ratingactioninfo',
            name='research_report',
            field=models.ForeignKey(blank=True, related_name='document_research_report', null=True, to='esma.AttachedDocument', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='ratingaction',
            name='rating_create_data',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingCreateData'),
        ),
        migrations.AddField(
            model_name='precedingpreliminaryrating',
            name='rating_info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingInfo'),
        ),
        migrations.AddField(
            model_name='leadanalystinfo',
            name='rating_action_info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingActionInfo'),
        ),
        migrations.AddField(
            model_name='issuerinfo',
            name='rating_info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingInfo'),
        ),
        migrations.AddField(
            model_name='instrumentinfo',
            name='rating_info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingInfo'),
        ),
        migrations.AddField(
            model_name='actiondateinfo',
            name='rating_action_info',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingActionInfo'),
        ),
    ]
