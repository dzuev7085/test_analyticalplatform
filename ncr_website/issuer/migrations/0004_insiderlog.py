# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rating_process', '0009_issuedecisionattribute_is_matured'),
        ('issuer', '0003_auto_20181106_1011'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsiderLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_added', models.DateTimeField(db_index=True)),
                ('date_removed', models.DateTimeField(null=True, blank=True, db_index=True)),
                ('addition_reason', models.CharField(max_length=255, db_index=True)),
                ('removal_reason', models.CharField(max_length=255, db_index=True)),
                ('insider', models.ForeignKey(blank=True, null=True, to='issuer.InsiderList', on_delete=django.db.models.deletion.PROTECT)),
                ('issuer', models.ForeignKey(to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT)),
                ('ncr_employee', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('rating_decision', models.ForeignKey(to='rating_process.RatingDecision', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
