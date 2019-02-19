# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0001_initial'),
        ('static_database_table', '0002_crainfo'),
        ('upload', '0001_initial'),
        ('rating_process', '0002_pressrelease'),
        ('esma', '0006_auto_20181012_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='QTActionDateInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('validity_date', models.DateTimeField()),
                ('communication_date', models.DateTimeField()),
                ('decision_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='QTInstrumentInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('isin_code', models.CharField(max_length=12, null=True, blank=True)),
                ('issuance_date', models.DateField(null=True, blank=True)),
                ('maturity_date', models.DateField(null=True, blank=True)),
                ('outstanding_issue_volume', models.DecimalField(null=True, max_digits=13, decimal_places=2, blank=True)),
                ('currency', models.ForeignKey(null=True, to='static_database_table.Currency', blank=True, on_delete=django.db.models.deletion.PROTECT)),
                ('issue', models.ForeignKey(to='issue.Issue', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='QTIssuerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lei_code', models.CharField(max_length=20)),
                ('issuer_name', models.CharField(max_length=90)),
            ],
        ),
        migrations.CreateModel(
            name='QTLeadAnalystInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lead_analyst_code', models.CharField(max_length=40)),
                ('country_model', models.ForeignKey(to='static_database_table.CountryRegion', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='QTPrecedingPreliminaryRating',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('preceding_preliminary_rating', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='QTRatingAction',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('action_type', models.IntegerField(choices=[(1, 'OR'), (2, 'PR'), (3, 'NW'), (4, 'UP'), (5, 'DG'), (6, 'AF'), (7, 'DF'), (8, 'SP'), (9, 'WD'), (10, 'OT'), (11, 'WR')])),
            ],
        ),
        migrations.CreateModel(
            name='QTRatingActionInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('rating_issuance_location', models.IntegerField(choices=[(1, 'I'), (2, 'E'), (3, 'T'), (4, 'O'), (5, 'N')])),
                ('rating_solicited_unsolicited', models.IntegerField(choices=[(1, 'S'), (2, 'U'), (3, 'P'), (4, 'N')])),
                ('press_release_flag', models.BooleanField(default=False)),
                ('research_report_flag', models.BooleanField(default=False)),
                ('press_release', models.ForeignKey(null=True, to='rating_process.PressRelease', blank=True, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='QTRatingCreateData',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('reporting_type', models.IntegerField(choices=[(1, 'NEW')])),
                ('rating_identifier', models.IntegerField()),
                ('rating_decision', models.ForeignKey(to='rating_process.RatingDecision', on_delete=django.db.models.deletion.PROTECT)),
                ('xml_file', models.ForeignKey(null=True, to='esma.XMLFile', on_delete=django.db.models.deletion.PROTECT, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='QTRatingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('responsible_cra_lei', models.CharField(max_length=20)),
                ('issuer_cra_lei', models.CharField(max_length=20)),
                ('rating_type', models.IntegerField(choices=[(1, 'C'), (2, 'S'), (3, 'T'), (4, 'O')])),
                ('rated_object', models.IntegerField(choices=[(1, 'ISR'), (2, 'INT')])),
                ('time_horizon', models.IntegerField(choices=[(1, 'L'), (2, 'S')])),
                ('industry', models.IntegerField(choices=[(1, 'FI'), (2, 'IN'), (3, 'CO')])),
                ('type_of_rating_for_erp', models.IntegerField(choices=[(1, 'NXI'), (2, 'EXI')], default=2)),
                ('relevant_for_cerep', models.BooleanField(default=False)),
                ('country_model', models.ForeignKey(to='static_database_table.CountryRegion', on_delete=django.db.models.deletion.PROTECT)),
                ('rating_action', models.OneToOneField(to='esma.QTRatingAction', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='QTRatingValue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('rating_value', models.IntegerField()),
                ('default_flag', models.BooleanField(default=False)),
                ('rating_action', models.OneToOneField(to='esma.QTRatingAction', on_delete=django.db.models.deletion.PROTECT)),
                ('rating_scale', models.ForeignKey(to='static_database_table.RatingScale', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.RemoveField(
            model_name='actiondateinfo',
            name='rating_action_info',
        ),
        migrations.RemoveField(
            model_name='instrumentinfo',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='instrumentinfo',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='instrumentinfo',
            name='rating_info',
        ),
        migrations.RemoveField(
            model_name='issuerinfo',
            name='rating_info',
        ),
        migrations.RemoveField(
            model_name='leadanalystinfo',
            name='country_model',
        ),
        migrations.RemoveField(
            model_name='leadanalystinfo',
            name='rating_action_info',
        ),
        migrations.RemoveField(
            model_name='precedingpreliminaryrating',
            name='rating_info',
        ),
        migrations.RemoveField(
            model_name='ratingaction',
            name='rating_create_data',
        ),
        migrations.RemoveField(
            model_name='ratingactioninfo',
            name='press_release',
        ),
        migrations.RemoveField(
            model_name='ratingactioninfo',
            name='rating_create_data',
        ),
        migrations.RemoveField(
            model_name='ratingactioninfo',
            name='research_report',
        ),
        migrations.RemoveField(
            model_name='ratingcreatedata',
            name='rating_decision',
        ),
        migrations.RemoveField(
            model_name='ratingcreatedata',
            name='xml_file',
        ),
        migrations.RemoveField(
            model_name='ratinginfo',
            name='country_model',
        ),
        migrations.RemoveField(
            model_name='ratinginfo',
            name='rating_action',
        ),
        migrations.RemoveField(
            model_name='ratingvalue',
            name='rating_action',
        ),
        migrations.RemoveField(
            model_name='ratingvalue',
            name='rating_scale',
        ),
        migrations.DeleteModel(
            name='ActionDateInfo',
        ),
        migrations.DeleteModel(
            name='InstrumentInfo',
        ),
        migrations.DeleteModel(
            name='IssuerInfo',
        ),
        migrations.DeleteModel(
            name='LeadAnalystInfo',
        ),
        migrations.DeleteModel(
            name='PrecedingPreliminaryRating',
        ),
        migrations.DeleteModel(
            name='RatingAction',
        ),
        migrations.DeleteModel(
            name='RatingActionInfo',
        ),
        migrations.DeleteModel(
            name='RatingCreateData',
        ),
        migrations.DeleteModel(
            name='RatingInfo',
        ),
        migrations.DeleteModel(
            name='RatingValue',
        ),
        migrations.AddField(
            model_name='qtratingactioninfo',
            name='rating_create_data',
            field=models.OneToOneField(to='esma.QTRatingCreateData', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtratingactioninfo',
            name='research_report',
            field=models.ForeignKey(null=True, to='upload.AnalyticalDocument', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtratingaction',
            name='rating_create_data',
            field=models.OneToOneField(to='esma.QTRatingCreateData', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtprecedingpreliminaryrating',
            name='rating_info',
            field=models.OneToOneField(to='esma.QTRatingInfo', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtleadanalystinfo',
            name='rating_action_info',
            field=models.OneToOneField(to='esma.QTRatingActionInfo', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtissuerinfo',
            name='rating_info',
            field=models.OneToOneField(to='esma.QTRatingInfo', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtinstrumentinfo',
            name='rating_info',
            field=models.OneToOneField(to='esma.QTRatingInfo', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='qtactiondateinfo',
            name='rating_action_info',
            field=models.OneToOneField(to='esma.QTRatingActionInfo', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
