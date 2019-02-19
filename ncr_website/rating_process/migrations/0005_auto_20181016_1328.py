# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0004_auto_20181015_1456'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecisionAttributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('is_new_preliminary', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=False)),
                ('is_lt_upgrade', models.BooleanField(default=False)),
                ('is_lt_downgrade', models.BooleanField(default=False)),
                ('is_lt_affirmation', models.BooleanField(default=False)),
                ('is_st_upgrade', models.BooleanField(default=False)),
                ('is_st_downgrade', models.BooleanField(default=False)),
                ('is_st_affirmation', models.BooleanField(default=False)),
                ('is_outlook_change', models.BooleanField(default=False)),
                ('is_watch', models.BooleanField(default=False)),
                ('is_suspension', models.BooleanField(default=False)),
                ('is_withdrawal', models.BooleanField(default=False)),
                ('is_default', models.BooleanField(default=False)),
                ('is_selective_default', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='decided_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='proposed_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='historicalratingdecisionissue',
            name='decided_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='historicalratingdecisionissue',
            name='proposed_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='decided_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='proposed_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='ratingdecisionissue',
            name='decided_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AlterField(
            model_name='ratingdecisionissue',
            name='proposed_lt',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')]),
        ),
        migrations.AddField(
            model_name='decisionattributes',
            name='rating_decision',
            field=models.OneToOneField(to='rating_process.RatingDecision', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
