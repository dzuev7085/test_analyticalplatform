# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0006_auto_20181022_1434'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='decisionattributes',
            options={'ordering': ['rating_decision__issuer__issuer_name_override', '-rating_decision__date_time_published']},
        ),
    ]
