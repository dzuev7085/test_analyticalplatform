# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0005_auto_20181108_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('lei', models.CharField(null=True, blank=True, max_length=20)),
                ('corporate_registration_id', models.CharField(null=True, blank=True, max_length=100)),
                ('issuer', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='issuer.Issuer')),
            ],
        ),
    ]
