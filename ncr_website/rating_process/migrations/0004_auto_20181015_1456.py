# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0003_auto_20181015_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalratingdecision',
            name='esma_rating_identifier',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='esma_rating_identifier',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
