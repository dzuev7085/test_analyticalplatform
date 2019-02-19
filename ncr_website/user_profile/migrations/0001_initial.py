# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('static_database_table', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalLeadAnalyst',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(default='2099-12-31')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical lead analyst',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalProfile',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('title', models.CharField(max_length=60)),
                ('phone_number', models.CharField(blank=True, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$', message="Phone number must be entered in the format: '+999999999999'. Up to 15 digits allowed.")], max_length=17)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('office_location', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='static_database_table.CountryRegion', null=True)),
                ('user', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical profile',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='LeadAnalyst',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(default='2099-12-31')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60)),
                ('phone_number', models.CharField(blank=True, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$', message="Phone number must be entered in the format: '+999999999999'. Up to 15 digits allowed.")], max_length=17)),
                ('office_location', models.ForeignKey(to='static_database_table.CountryRegion', default=166, on_delete=django.db.models.deletion.PROTECT)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='leadanalyst',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user_profile.Profile'),
        ),
        migrations.AddField(
            model_name='historicalleadanalyst',
            name='profile',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='user_profile.Profile', null=True),
        ),
    ]
