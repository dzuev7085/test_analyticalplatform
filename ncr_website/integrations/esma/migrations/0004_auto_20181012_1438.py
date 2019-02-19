# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0003_auto_20181012_1306'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ratinginfo',
            old_name='CountryRegion_model',
            new_name='country_model',
        ),
    ]
