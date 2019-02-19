# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0002_pressrelease'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalratingdecision',
            name='date_time_communicated_issuer',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalratingdecision',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalratingdecision',
            name='previous_rating',
            field=models.ForeignKey(blank=True, to='rating_process.RatingDecision', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='date_time_communicated_issuer',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='previous_rating',
            field=models.ForeignKey(blank=True, to='rating_process.RatingDecision', null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
