# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_database_table', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CRAInfo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('cra_name', models.CharField(max_length=90)),
                ('cra_description', models.TextField(max_length=500)),
                ('cra_methodology', models.TextField(max_length=4000)),
                ('cra_methodology_webpage_link', models.TextField(max_length=300)),
                ('solicited_unsolicited_rating_policy_description', models.TextField(max_length=500)),
                ('subsidiary_rating_policy', models.TextField(max_length=500)),
                ('global_reporting_scope_flag', models.IntegerField(choices=[(1, 'Y'), (2, 'N')])),
                ('definition_default', models.TextField(max_length=2000)),
                ('cra_website_link', models.TextField(max_length=40)),
            ],
        ),
    ]
