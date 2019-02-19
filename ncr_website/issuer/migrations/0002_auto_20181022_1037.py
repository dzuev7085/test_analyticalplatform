# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalinsiderlist',
            name='contact_type',
            field=models.IntegerField(help_text="Leave as '----' if not primary or secondary contact.", choices=[(1, 'Primary contact'), (2, 'Secondary contact')], blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalinsiderlist',
            name='date_deletion',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalinsiderlist',
            name='first_name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalinsiderlist',
            name='last_name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalinsiderlist',
            name='role',
            field=models.CharField(max_length=100, db_index=True, help_text="Eg 'Debt analyst' or 'Legal counsel'"),
        ),
        migrations.AlterField(
            model_name='insiderlist',
            name='contact_type',
            field=models.IntegerField(help_text="Leave as '----' if not primary or secondary contact.", choices=[(1, 'Primary contact'), (2, 'Secondary contact')], blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='insiderlist',
            name='date_deletion',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='insiderlist',
            name='first_name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='insiderlist',
            name='last_name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='insiderlist',
            name='role',
            field=models.CharField(max_length=100, db_index=True, help_text="Eg 'Debt analyst' or 'Legal counsel'"),
        ),
        migrations.AlterField(
            model_name='issuer',
            name='issuer_name_override',
            field=models.CharField(unique=True, max_length=128, db_index=True),
        ),
    ]
