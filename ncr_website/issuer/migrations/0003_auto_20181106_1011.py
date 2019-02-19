# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0002_auto_20181022_1037'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalissuer',
            old_name='LEI',
            new_name='lei',
        ),
        migrations.RenameField(
            model_name='issuer',
            old_name='LEI',
            new_name='lei',
        ),
    ]
