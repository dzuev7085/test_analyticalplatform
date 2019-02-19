# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('static_database_table', '0004_auto_20181026_1807'),
        ('issuer', '0006_identifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('country', models.ForeignKey(to='static_database_table.CountryRegion', blank=True, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('issuer', models.OneToOneField(to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
