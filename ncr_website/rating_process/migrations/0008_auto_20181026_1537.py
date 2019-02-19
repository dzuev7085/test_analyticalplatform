# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import tinymce.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0003_auto_20181025_1118'),
        ('rating_process', '0007_auto_20181024_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalIssueDecision',
            fields=[
                ('id', models.IntegerField(auto_created=True, db_index=True, verbose_name='ID', blank=True)),
                ('is_preliminary', models.BooleanField(default=False)),
                ('is_current', models.BooleanField(default=True, db_index=True)),
                ('date_time_committee', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_published', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_communicated_issuer', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_deleted', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_creation', models.DateTimeField(db_index=True, blank=True, editable=False)),
                ('decided_lt', models.IntegerField(choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')], null=True, blank=True)),
                ('rationale', tinymce.models.HTMLField(null=True, blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='+')),
                ('history_user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True, related_name='+')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='issue.Issue', null=True, related_name='+')),
            ],
            options={
                'verbose_name': 'historical issue decision',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='IssueDecision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('is_preliminary', models.BooleanField(default=False)),
                ('is_current', models.BooleanField(default=True, db_index=True)),
                ('date_time_committee', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_published', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_communicated_issuer', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_deleted', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('date_time_creation', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('decided_lt', models.IntegerField(choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (20, 'D'), (21, 'SD'), (200, 'NR')], null=True, blank=True)),
                ('rationale', tinymce.models.HTMLField(null=True, blank=True)),
                ('approved_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='issue.Issue')),
                ('previous_rating', models.ForeignKey(blank=True, to='rating_process.IssueDecision', null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('rating_decision_issue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecisionIssue')),
            ],
        ),
        migrations.CreateModel(
            name='IssueDecisionAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('is_new_preliminary', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=False)),
                ('is_lt_upgrade', models.BooleanField(default=False)),
                ('is_lt_downgrade', models.BooleanField(default=False)),
                ('is_lt_affirmation', models.BooleanField(default=False)),
                ('is_suspension', models.BooleanField(default=False)),
                ('is_withdrawal', models.BooleanField(default=False)),
                ('is_default', models.BooleanField(default=False)),
                ('is_selective_default', models.BooleanField(default=False)),
                ('rating_decision_issue', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='rating_process.IssueDecision')),
            ],
        ),
        migrations.AddField(
            model_name='historicalissuedecision',
            name='previous_rating',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='rating_process.IssueDecision', null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='historicalissuedecision',
            name='rating_decision_issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='rating_process.RatingDecisionIssue', null=True, related_name='+'),
        ),
    ]
