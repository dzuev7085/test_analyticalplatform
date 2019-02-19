# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0004_insiderlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalissuer',
            name='parent_company',
            field=models.ForeignKey(related_name='+', null=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='issuer.Issuer'),
        ),
        migrations.AddField(
            model_name='issuer',
            name='parent_company',
            field=models.ForeignKey(null=True, to='issuer.Issuer', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
