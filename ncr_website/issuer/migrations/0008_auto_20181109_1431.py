# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0007_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issuer',
            options={'ordering': ['legal_name']},
        ),
        migrations.RenameField(
            model_name='historicalissuer',
            old_name='issuer_name_override',
            new_name='legal_name',
        ),
        migrations.RenameField(
            model_name='issuer',
            old_name='issuer_name_override',
            new_name='legal_name',
        ),
        migrations.AddField(
            model_name='historicalissuer',
            name='short_name',
            field=models.CharField(max_length=128, blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='issuer',
            name='short_name',
            field=models.CharField(max_length=128, blank=True, db_index=True, null=True),
        ),
    ]
