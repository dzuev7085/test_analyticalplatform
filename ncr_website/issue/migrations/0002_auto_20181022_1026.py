# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalissue',
            name='maturity',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='maturity',
            field=models.DateField(db_index=True),
        ),
    ]
