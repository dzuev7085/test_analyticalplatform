# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyticaldocument',
            name='uploaded_at',
            field=models.DateTimeField(db_index=True, auto_now_add=True),
        ),
    ]
