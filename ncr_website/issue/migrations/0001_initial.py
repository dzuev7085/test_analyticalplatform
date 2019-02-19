# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('static_database_table', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalIssue',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('isin', models.CharField(db_index=True, max_length=12)),
                ('name', models.CharField(max_length=132)),
                ('ticker', models.CharField(blank=True, max_length=32, null=True, db_index=True)),
                ('disbursement', models.DateField(blank=True, null=True)),
                ('maturity', models.DateField()),
                ('interest', models.CharField(blank=True, max_length=32, null=True)),
                ('amount', models.DecimalField(blank=True, max_digits=13, null=True, decimal_places=2)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('currency', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='static_database_table.Currency', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('issuer', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issuer.Issuer', null=True)),
            ],
            options={
                'verbose_name': 'historical issue',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isin', models.CharField(max_length=12, unique=True)),
                ('name', models.CharField(max_length=132)),
                ('ticker', models.CharField(blank=True, max_length=32, unique=True, null=True)),
                ('disbursement', models.DateField(blank=True, null=True)),
                ('maturity', models.DateField()),
                ('interest', models.CharField(blank=True, max_length=32, null=True)),
                ('amount', models.DecimalField(blank=True, max_digits=13, null=True, decimal_places=2)),
                ('currency', models.ForeignKey(related_name='issue_currency_link', blank=True, to='static_database_table.Currency', null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('issuer', models.ForeignKey(related_name='issue_issuer_link', to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90)),
                ('description', models.TextField(max_length=500)),
                ('start_date', models.DateField(default='2018-09-29')),
                ('end_date', models.DateField(default='2099-12-31')),
            ],
        ),
        migrations.CreateModel(
            name='Seniority',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90)),
                ('description', models.TextField(max_length=500, unique=True)),
                ('start_date', models.DateField(default='2018-09-29')),
                ('end_date', models.DateField(default='2099-12-31')),
            ],
        ),
        migrations.CreateModel(
            name='SeniorityLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='seniority',
            name='seniority_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='issue.SeniorityLevel'),
        ),
        migrations.AddField(
            model_name='issue',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='issue.Program'),
        ),
        migrations.AddField(
            model_name='issue',
            name='seniority',
            field=models.ForeignKey(related_name='issue_seniority_link', to='issue.Seniority', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='historicalissue',
            name='program',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issue.Program', null=True),
        ),
        migrations.AddField(
            model_name='historicalissue',
            name='seniority',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issue.Seniority', null=True),
        ),
    ]
