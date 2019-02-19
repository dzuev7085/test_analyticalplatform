# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_database_table', '0002_crainfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countryregion',
            name='iso_31661_alpha_2',
            field=models.CharField(db_index=True, max_length=2),
        ),
    ]
