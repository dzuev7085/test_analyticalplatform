# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CountryRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('iso_31661_alpha_2', models.CharField(max_length=2)),
                ('iso_31661_alpha_3', models.CharField(max_length=3)),
                ('iso_31661_alpha_3_country_code', models.IntegerField()),
                ('iso_3166_2', models.CharField(max_length=13)),
                ('region', models.CharField(blank=True, max_length=8, null=True)),
                ('sub_region', models.CharField(blank=True, max_length=31, null=True)),
                ('intermediate_region', models.CharField(blank=True, max_length=31, null=True)),
                ('region_code', models.IntegerField(blank=True, null=True)),
                ('sub_region_code', models.IntegerField(blank=True, null=True)),
                ('intermediate_region_code', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('currency_code_alpha_3', models.CharField(max_length=3)),
                ('currency_code_alpha_3_currency_code', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GICSIndustry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('industry', models.IntegerField()),
                ('industry_name', models.CharField(max_length=100)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GICSIndustryGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('industry_group', models.IntegerField()),
                ('industry_group_name', models.CharField(max_length=100)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GICSSector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sector', models.IntegerField()),
                ('sector_name', models.CharField(max_length=100)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GICSSubIndustry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sub_industry', models.IntegerField()),
                ('sub_industry_name', models.CharField(max_length=100)),
                ('sub_industry_description', models.CharField(max_length=999)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IssuerRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90)),
                ('description', models.TextField(max_length=500)),
                ('standard', models.IntegerField(choices=[(1, 'IR'), (2, 'DT'), (3, 'OT')])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='RatingCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('label', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RatingNotch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('label', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
                ('rating_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='static_database_table.RatingCategory')),
            ],
        ),
        migrations.CreateModel(
            name='RatingScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RatingScope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_horizon', models.IntegerField(choices=[(1, 'L'), (2, 'S')])),
                ('rating_type', models.IntegerField(choices=[(1, 'C'), (2, 'S'), (3, 'T'), (4, 'O')])),
                ('rating_scale_scope', models.IntegerField(choices=[(1, 'PR'), (2, 'FR'), (3, 'BT')])),
                ('relevant_for_cerep_flag', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('rating_scale', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='static_database_table.RatingScale')),
            ],
        ),
        migrations.AddField(
            model_name='ratingcategory',
            name='rating_scale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='static_database_table.RatingScale'),
        ),
    ]
