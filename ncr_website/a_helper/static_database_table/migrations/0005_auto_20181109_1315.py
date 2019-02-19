# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('static_database_table', '0004_auto_20181026_1807'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gicsindustry',
            options={'ordering': ['code']},
        ),
        migrations.AlterModelOptions(
            name='gicsindustrygroup',
            options={'ordering': ['code']},
        ),
        migrations.AlterModelOptions(
            name='gicssector',
            options={'ordering': ['code']},
        ),
        migrations.AlterModelOptions(
            name='gicssubindustry',
            options={'ordering': ['code']},
        ),
        migrations.RenameField(
            model_name='gicsindustry',
            old_name='industry',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='gicsindustry',
            old_name='industry_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='gicsindustrygroup',
            old_name='industry_group',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='gicsindustrygroup',
            old_name='industry_group_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='gicssector',
            old_name='sector',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='gicssector',
            old_name='sector_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='gicssubindustry',
            old_name='sub_industry',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='gicssubindustry',
            old_name='sub_industry_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='gicssubindustry',
            old_name='sub_industry_name',
            new_name='name',
        ),
        migrations.AddField(
            model_name='gicsindustry',
            name='industry_group',
            field=models.ForeignKey(null=True, blank=True, to='static_database_table.GICSIndustryGroup', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='gicsindustrygroup',
            name='sector',
            field=models.ForeignKey(null=True, blank=True, to='static_database_table.GICSSector', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='gicssubindustry',
            name='industry',
            field=models.ForeignKey(null=True, blank=True, to='static_database_table.GICSIndustry', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
