# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import integrations.esma.models.xml_file
import config.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CRAInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('cra_info_code', models.CharField(max_length=10)),
                ('cra_name', models.CharField(max_length=90)),
                ('cra_description', models.TextField(max_length=500)),
                ('cra_methodology', models.TextField(max_length=4000)),
                ('cra_methodology_webpage_link', models.TextField(max_length=300)),
                ('solicited_unsolicited_rating_policy_description', models.TextField(max_length=500)),
                ('subsidiary_rating_policy', models.TextField(max_length=500)),
                ('global_reporting_scope_flag', models.IntegerField(choices=[(1, 'Y'), (2, 'N')])),
                ('definition_default', models.TextField(max_length=2000)),
                ('cra_website_link', models.TextField(max_length=40)),
                ('reporting_type_info', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='esma.ReportingTypeInfo', blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='debtclassification',
            name='sent_to_esma',
        ),
        migrations.RemoveField(
            model_name='issueprogram',
            name='sent_to_esma',
        ),
        migrations.RemoveField(
            model_name='issuerrating',
            name='sent_to_esma',
        ),
        migrations.RemoveField(
            model_name='leadanalyst',
            name='sent_to_esma',
        ),
        migrations.RemoveField(
            model_name='ratingscale',
            name='sent_to_esma',
        ),
        migrations.AddField(
            model_name='xmlfile',
            name='response_file',
            field=models.FileField(blank=True, upload_to=integrations.esma.models.xml_file.get_upload_to, null=True, storage=config.storage_backends.ESMAMediaStorage()),
        ),
        migrations.AddField(
            model_name='xmlfile',
            name='status_code',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'fail'), (1, 'success')]),
        ),
        migrations.AddField(
            model_name='crainfo',
            name='xml_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='esma.XMLFile', blank=True, null=True),
        ),
    ]
