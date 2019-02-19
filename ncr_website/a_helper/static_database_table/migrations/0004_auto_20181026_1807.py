# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_database_table', '0003_auto_20181024_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gicssector',
            name='sector',
            field=models.IntegerField(db_index=True),
        ),
    ]
