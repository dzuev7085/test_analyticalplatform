# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0008_auto_20181026_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuedecisionattribute',
            name='is_matured',
            field=models.BooleanField(default=False),
        ),
    ]
