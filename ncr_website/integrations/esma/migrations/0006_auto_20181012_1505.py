# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0005_auto_20181012_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attacheddocument',
            name='document',
        ),
        migrations.AlterField(
            model_name='ratingactioninfo',
            name='press_release',
            field=models.ForeignKey(null=True, to='rating_process.PressRelease', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='ratingactioninfo',
            name='research_report',
            field=models.ForeignKey(null=True, to='upload.AnalyticalDocument', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.DeleteModel(
            name='AttachedDocument',
        ),
    ]
