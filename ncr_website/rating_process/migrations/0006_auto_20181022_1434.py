# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0005_auto_20181016_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalratingdecision',
            name='process_step',
            field=models.IntegerField(choices=[(1, 'setup'), (2, 'pre_committee'), (3, 'analytical_phase'), (4, 'post_committee'), (5, 'editor_phase'), (6, 'issuer_confirmation_phase'), (7, 'analyst_final_approval_phase'), (8, 'chair_final_approval_phase'), (9, 'publishing_phase'), (10, 'publishing_phase_done')], db_index=True, default=1),
        ),
        migrations.AddField(
            model_name='ratingdecision',
            name='process_step',
            field=models.IntegerField(choices=[(1, 'setup'), (2, 'pre_committee'), (3, 'analytical_phase'), (4, 'post_committee'), (5, 'editor_phase'), (6, 'issuer_confirmation_phase'), (7, 'analyst_final_approval_phase'), (8, 'chair_final_approval_phase'), (9, 'publishing_phase'), (10, 'publishing_phase_done')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='analytical_phase_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='editor_review_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='final_sign_off_analyst_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='final_sign_off_chair_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='issuer_confirmation_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='post_committee_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='pre_committee_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='process_ended',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprocess',
            name='setup_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='date_time_committee',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='date_time_communicated_issuer',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='date_time_creation',
            field=models.DateTimeField(editable=False, blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='date_time_deleted',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='date_time_published',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalratingdecision',
            name='is_current',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='internalscoredatafactor',
            name='name',
            field=models.CharField(max_length=128, db_index=True),
        ),
        migrations.AlterField(
            model_name='internalscoredatasubfactor',
            name='sort_order',
            field=models.IntegerField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='jobmember',
            name='committee_member_confirmed',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='process',
            name='analytical_phase_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='editor_review_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='final_sign_off_analyst_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='final_sign_off_chair_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='issuer_confirmation_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='post_committee_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='pre_committee_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='process_ended',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='process',
            name='setup_done',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='date_time_committee',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='date_time_communicated_issuer',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='date_time_creation',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='date_time_deleted',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='date_time_published',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='ratingdecision',
            name='is_current',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='stage',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
    ]
