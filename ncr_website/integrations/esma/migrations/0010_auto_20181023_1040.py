# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0009_auto_20181018_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='qtratingcreatedata',
            name='hash',
            field=models.CharField(blank=True, max_length='32', db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='reportingtypeinfo',
            name='hash',
            field=models.CharField(blank=True, max_length='32', db_index=True, null=True),
        ),
    ]
