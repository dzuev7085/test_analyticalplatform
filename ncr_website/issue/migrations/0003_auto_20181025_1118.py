# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0002_auto_20181022_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalissue',
            name='is_matured',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='issue',
            name='is_matured',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
