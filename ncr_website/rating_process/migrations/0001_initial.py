# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('methodology', '0001_initial'),
        ('issuer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answered_on', models.DateTimeField(blank=True, null=True)),
                ('answer_correct', models.BooleanField(default=False)),
                ('answered_by', models.ForeignKey(related_name='control_question_answered_by', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ('rating_decision', 'question__question'),
            },
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalControlQuestion',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('answered_on', models.DateTimeField(blank=True, null=True)),
                ('answer_correct', models.BooleanField(default=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('answered_by', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical control question',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalInternalScoreData',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('weight', models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], null=True)),
                ('weight_edit_allowed', models.BooleanField(default=False)),
                ('proposed_score', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)], null=True, default=False, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-')])),
                ('decided_score', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)], null=True, default=False, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-')])),
                ('proposed_notch_adjustment', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(10)], null=True, default=False, choices=[(5, '+5'), (4, '+4'), (3, '+3'), (2, '+2'), (1, '+1'), (0, '0'), (-1, '-1'), (-2, '-2'), (-3, '-3'), (-4, '-4'), (-5, '-5')])),
                ('decided_notch_adjustment', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(10)], null=True, default=False, choices=[(5, '+5'), (4, '+4'), (3, '+3'), (2, '+2'), (1, '+1'), (0, '0'), (-1, '-1'), (-2, '-2'), (-3, '-3'), (-4, '-4'), (-5, '-5')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical internal score data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalProcess',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('process_started', models.DateTimeField(editable=False, blank=True)),
                ('setup_done', models.DateTimeField(blank=True, null=True)),
                ('pre_committee_done', models.DateTimeField(blank=True, null=True)),
                ('analytical_phase_done', models.DateTimeField(blank=True, null=True)),
                ('post_committee_done', models.DateTimeField(blank=True, null=True)),
                ('editor_review_done', models.DateTimeField(blank=True, null=True)),
                ('issuer_confirmation_done', models.DateTimeField(blank=True, null=True)),
                ('final_sign_off_analyst_done', models.DateTimeField(blank=True, null=True)),
                ('final_sign_off_chair_done', models.DateTimeField(blank=True, null=True)),
                ('process_ended', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical process',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalRatingDecision',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('is_preliminary', models.BooleanField(default=False)),
                ('is_unsolicited', models.BooleanField(default=False)),
                ('event', tinymce.models.HTMLField(blank=True, null=True)),
                ('date_time_committee', models.DateTimeField(blank=True, null=True)),
                ('date_time_committee_confirmed', models.BooleanField(default=False)),
                ('date_time_published', models.DateTimeField(blank=True, null=True)),
                ('date_time_deleted', models.DateTimeField(blank=True, null=True)),
                ('date_time_creation', models.DateTimeField(editable=False, blank=True)),
                ('proposed_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('proposed_lt_outlook', models.IntegerField(blank=True, null=True, choices=[(1, 'Positive'), (2, 'Stable'), (3, 'Negative'), (4, 'Watch developing'), (5, 'Watch positive'), (6, 'Watch negative'), (7, 'NR')])),
                ('proposed_st', models.IntegerField(blank=True, null=True, choices=[(1, 'N-1+'), (2, 'N-1'), (3, 'N-2'), (4, 'N-3'), (5, 'N-4'), (6, 'SD'), (7, 'D'), (8, 'NR')])),
                ('decided_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('decided_lt_outlook', models.IntegerField(blank=True, null=True, choices=[(1, 'Positive'), (2, 'Stable'), (3, 'Negative'), (4, 'Watch developing'), (5, 'Watch positive'), (6, 'Watch negative'), (7, 'NR')])),
                ('decided_st', models.IntegerField(blank=True, null=True, choices=[(1, 'N-1+'), (2, 'N-1'), (3, 'N-2'), (4, 'N-3'), (5, 'N-4'), (6, 'SD'), (7, 'D'), (8, 'NR')])),
                ('chair_confirmed', models.BooleanField(default=False)),
                ('recommendation_rationale', tinymce.models.HTMLField(blank=True, null=True)),
                ('committee_comments', tinymce.models.HTMLField(blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('chair', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('event_type', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.EventType', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('initiated_by', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('issuer', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issuer.Issuer', null=True)),
                ('primary_analyst', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical rating decision',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalRatingDecisionIssue',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('proposed_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('decided_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical rating decision issue',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='InternalScoreData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], null=True)),
                ('weight_edit_allowed', models.BooleanField(default=False)),
                ('proposed_score', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)], null=True, default=False, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-')])),
                ('decided_score', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)], null=True, default=False, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-')])),
                ('proposed_notch_adjustment', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(10)], null=True, default=False, choices=[(5, '+5'), (4, '+4'), (3, '+3'), (2, '+2'), (1, '+1'), (0, '0'), (-1, '-1'), (-2, '-2'), (-3, '-3'), (-4, '-4'), (-5, '-5')])),
                ('decided_notch_adjustment', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(10)], null=True, default=False, choices=[(5, '+5'), (4, '+4'), (3, '+3'), (2, '+2'), (1, '+1'), (0, '0'), (-1, '-1'), (-2, '-2'), (-3, '-3'), (-4, '-4'), (-5, '-5')])),
            ],
        ),
        migrations.CreateModel(
            name='InternalScoreDataFactor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='InternalScoreDataSubfactor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('sort_order', models.IntegerField(blank=True, null=True)),
                ('factor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.InternalScoreDataFactor')),
            ],
        ),
        migrations.CreateModel(
            name='JobMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('committee_member_confirmed', models.BooleanField(default=False)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.Group')),
                ('member', models.ForeignKey(related_name='committee_member_committee_member', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('process_started', models.DateTimeField(auto_now_add=True)),
                ('setup_done', models.DateTimeField(blank=True, null=True)),
                ('pre_committee_done', models.DateTimeField(blank=True, null=True)),
                ('analytical_phase_done', models.DateTimeField(blank=True, null=True)),
                ('post_committee_done', models.DateTimeField(blank=True, null=True)),
                ('editor_review_done', models.DateTimeField(blank=True, null=True)),
                ('issuer_confirmation_done', models.DateTimeField(blank=True, null=True)),
                ('final_sign_off_analyst_done', models.DateTimeField(blank=True, null=True)),
                ('final_sign_off_chair_done', models.DateTimeField(blank=True, null=True)),
                ('process_ended', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=False)),
                ('question', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='RatingDecision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_preliminary', models.BooleanField(default=False)),
                ('is_unsolicited', models.BooleanField(default=False)),
                ('event', tinymce.models.HTMLField(blank=True, null=True)),
                ('date_time_committee', models.DateTimeField(blank=True, null=True)),
                ('date_time_committee_confirmed', models.BooleanField(default=False)),
                ('date_time_published', models.DateTimeField(blank=True, null=True)),
                ('date_time_deleted', models.DateTimeField(blank=True, null=True)),
                ('date_time_creation', models.DateTimeField(auto_now_add=True)),
                ('proposed_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('proposed_lt_outlook', models.IntegerField(blank=True, null=True, choices=[(1, 'Positive'), (2, 'Stable'), (3, 'Negative'), (4, 'Watch developing'), (5, 'Watch positive'), (6, 'Watch negative'), (7, 'NR')])),
                ('proposed_st', models.IntegerField(blank=True, null=True, choices=[(1, 'N-1+'), (2, 'N-1'), (3, 'N-2'), (4, 'N-3'), (5, 'N-4'), (6, 'SD'), (7, 'D'), (8, 'NR')])),
                ('decided_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('decided_lt_outlook', models.IntegerField(blank=True, null=True, choices=[(1, 'Positive'), (2, 'Stable'), (3, 'Negative'), (4, 'Watch developing'), (5, 'Watch positive'), (6, 'Watch negative'), (7, 'NR')])),
                ('decided_st', models.IntegerField(blank=True, null=True, choices=[(1, 'N-1+'), (2, 'N-1'), (3, 'N-2'), (4, 'N-3'), (5, 'N-4'), (6, 'SD'), (7, 'D'), (8, 'NR')])),
                ('chair_confirmed', models.BooleanField(default=False)),
                ('recommendation_rationale', tinymce.models.HTMLField(blank=True, null=True)),
                ('committee_comments', tinymce.models.HTMLField(blank=True, null=True)),
                ('chair', models.ForeignKey(related_name='rating_decision_chair', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.EventType')),
                ('initiated_by', models.ForeignKey(related_name='rating_decision_initiated_by', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('issuer', models.ForeignKey(related_name='rating_decision_issuer', on_delete=django.db.models.deletion.PROTECT, to='issuer.Issuer')),
                ('primary_analyst', models.ForeignKey(related_name='rating_decision_primary_analyst', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['issuer', 'date_time_committee', '-date_time_creation'],
            },
        ),
        migrations.CreateModel(
            name='RatingDecisionInsiderLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='issuer.InsiderList')),
                ('rating_decision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision')),
            ],
        ),
        migrations.CreateModel(
            name='RatingDecisionIssue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('proposed_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('decided_lt', models.IntegerField(blank=True, null=True, choices=[(1, 'AAA'), (2, 'AA+'), (3, 'AA'), (4, 'AA-'), (5, 'A+'), (6, 'A'), (7, 'A-'), (8, 'BBB+'), (9, 'BBB'), (10, 'BBB-'), (11, 'BB+'), (12, 'BB'), (13, 'BB-'), (14, 'B+'), (15, 'B'), (16, 'B-'), (17, 'CCC'), (18, 'CC'), (19, 'C'), (100, 'SD'), (101, 'D'), (200, 'NR')])),
                ('rating_decision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision')),
                ('seniority', models.ForeignKey(related_name='rating_decision_issue_seniority_link', on_delete=django.db.models.deletion.PROTECT, to='issue.Seniority')),
            ],
        ),
        migrations.CreateModel(
            name='RatingDecisionMethodologyLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('methodology', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='methodology.Methodology')),
                ('rating_decision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision')),
            ],
        ),
        migrations.CreateModel(
            name='RatingType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Tmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('editor_admin_control_link', models.CharField(blank=True, max_length=255, null=True)),
                ('issuer_admin_control_link', models.CharField(blank=True, max_length=255, null=True)),
                ('rating_decision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision')),
            ],
        ),
        migrations.CreateModel(
            name='ViewLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time_downloaded', models.DateTimeField(auto_now_add=True)),
                ('downloaded_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('rating_decision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision')),
            ],
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='rating_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingType'),
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='secondary_analyst',
            field=models.ForeignKey(related_name='rating_decision_secondary_analyst', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='question',
            name='stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.Stage'),
        ),
        migrations.AddField(
            model_name='process',
            name='rating_decision',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision'),
        ),
        migrations.AddField(
            model_name='jobmember',
            name='rating_decision',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision'),
        ),
        migrations.AddField(
            model_name='jobmember',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.Role'),
        ),
        migrations.AddField(
            model_name='internalscoredata',
            name='rating_decision',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision'),
        ),
        migrations.AddField(
            model_name='internalscoredata',
            name='subfactor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.InternalScoreDataSubfactor'),
        ),
        migrations.AddField(
            model_name='historicalratingdecisionissue',
            name='rating_decision',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.RatingDecision', null=True),
        ),
        migrations.AddField(
            model_name='historicalratingdecisionissue',
            name='seniority',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issue.Seniority', null=True),
        ),
        migrations.AddField(
            model_name='historicalratingdecision',
            name='rating_type',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.RatingType', null=True),
        ),
        migrations.AddField(
            model_name='historicalratingdecision',
            name='secondary_analyst',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalprocess',
            name='rating_decision',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.RatingDecision', null=True),
        ),
        migrations.AddField(
            model_name='historicalinternalscoredata',
            name='rating_decision',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.RatingDecision', null=True),
        ),
        migrations.AddField(
            model_name='historicalinternalscoredata',
            name='subfactor',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.InternalScoreDataSubfactor', null=True),
        ),
        migrations.AddField(
            model_name='historicalcontrolquestion',
            name='question',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.Question', null=True),
        ),
        migrations.AddField(
            model_name='historicalcontrolquestion',
            name='rating_decision',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='rating_process.RatingDecision', null=True),
        ),
        migrations.AddField(
            model_name='controlquestion',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.Question'),
        ),
        migrations.AddField(
            model_name='controlquestion',
            name='rating_decision',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision'),
        ),
    ]
