# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0004_auto_20181012_1438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leadanalystinfo',
            old_name='CountryRegion_model',
            new_name='country_model',
        ),
    ]
