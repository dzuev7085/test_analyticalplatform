# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esma', '0007_auto_20181012_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qtratingcreatedata',
            name='xml_file',
            field=models.OneToOneField(null=True, blank=True, to='esma.XMLFile', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
