# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import integrations.esma.models.xml_file
import django.db.models.deletion
import config.storage_backends


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DebtClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('sent_to_esma', models.DateTimeField(blank=True, null=True)),
                ('debt_classification_code', models.CharField(max_length=10)),
                ('debt_classification_name', models.CharField(max_length=90)),
                ('debt_classification_description', models.TextField(max_length=500)),
                ('seniority', models.IntegerField()),
                ('debt_classification_start_date', models.DateField()),
                ('debt_classification_end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='IssueProgram',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('sent_to_esma', models.DateTimeField(blank=True, null=True)),
                ('program_code', models.CharField(max_length=10)),
                ('program_name', models.CharField(max_length=90)),
                ('program_description', models.TextField(max_length=500)),
                ('program_start_date', models.DateField()),
                ('program_end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='IssuerRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('sent_to_esma', models.DateTimeField(blank=True, null=True)),
                ('rating_type_code', models.CharField(max_length=10)),
                ('rating_type_name', models.CharField(max_length=90)),
                ('rating_type_description', models.TextField(max_length=500)),
                ('rating_type_standard', models.IntegerField(choices=[(1, 'IR'), (2, 'DT'), (3, 'OT')])),
                ('rating_type_start_date', models.DateField()),
                ('rating_type_end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='LeadAnalyst',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead_analyst_code', models.CharField(max_length=40)),
                ('lead_analyst_name', models.CharField(max_length=90)),
                ('lead_analyst_start_date', models.DateField()),
                ('lead_analyst_end_date', models.DateField()),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('sent_to_esma', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RatingCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating_category_code', models.CharField(max_length=10)),
                ('value', models.IntegerField()),
                ('label', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RatingNotch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating_notch_code', models.CharField(max_length=10)),
                ('value', models.IntegerField()),
                ('label', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
                ('rating_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingCategory')),
            ],
        ),
        migrations.CreateModel(
            name='RatingScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('sent_to_esma', models.DateTimeField(blank=True, null=True)),
                ('rating_scale_code', models.CharField(max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RatingScope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating_scope_code', models.CharField(max_length=10)),
                ('time_horizon', models.IntegerField(choices=[(1, 'L'), (2, 'S')])),
                ('rating_type', models.IntegerField(choices=[(1, 'C'), (2, 'S'), (3, 'T'), (4, 'O')])),
                ('rating_scale_scope', models.IntegerField(choices=[(1, 'PR'), (2, 'FR'), (3, 'BT')])),
                ('relevant_for_cerep_flag', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('rating_scale', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingScale')),
            ],
        ),
        migrations.CreateModel(
            name='ReportingTypeInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reporting_type', models.IntegerField(choices=[(1, 'NEW'), (2, 'CHG')])),
                ('change_reason', models.IntegerField(blank=True, null=True, choices=[(1, 'C'), (2, 'U')])),
                ('reporting_reason', models.TextField(blank=True, max_length='300', null=True)),
                ('hash', models.CharField(blank=True, max_length='32', null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='XMLFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_created', models.DateTimeField(auto_now_add=True)),
                ('file_type', models.IntegerField(choices=[(1, 'DATQXX'), (2, 'DATRXX')])),
                ('sequence_number', models.IntegerField(editable=False, blank=True, null=True)),
                ('document_location', models.FileField(blank=True, upload_to=integrations.esma.models.xml_file.get_upload_to, null=True, storage=config.storage_backends.ESMAMediaStorage())),
            ],
        ),
        migrations.AddField(
            model_name='ratingscale',
            name='reporting_type_info',
            field=models.ForeignKey(to='esma.ReportingTypeInfo', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='ratingscale',
            name='xml_file',
            field=models.ForeignKey(to='esma.XMLFile', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='ratingcategory',
            name='rating_scale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='esma.RatingScale'),
        ),
        migrations.AddField(
            model_name='leadanalyst',
            name='reporting_type_info',
            field=models.ForeignKey(to='esma.ReportingTypeInfo', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='leadanalyst',
            name='xml_file',
            field=models.ForeignKey(to='esma.XMLFile', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='issuerrating',
            name='reporting_type_info',
            field=models.ForeignKey(to='esma.ReportingTypeInfo', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='issuerrating',
            name='xml_file',
            field=models.ForeignKey(to='esma.XMLFile', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='issueprogram',
            name='reporting_type_info',
            field=models.ForeignKey(to='esma.ReportingTypeInfo', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='issueprogram',
            name='xml_file',
            field=models.ForeignKey(to='esma.XMLFile', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='debtclassification',
            name='reporting_type_info',
            field=models.ForeignKey(to='esma.ReportingTypeInfo', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
        migrations.AddField(
            model_name='debtclassification',
            name='xml_file',
            field=models.ForeignKey(to='esma.XMLFile', blank=True, on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
    ]
