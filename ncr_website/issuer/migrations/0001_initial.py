# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
import tinymce.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('static_database_table', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analyst',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalAnalyst',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical analyst',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalInsiderList',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('company', models.CharField(blank=True, max_length=100, null=True, help_text='If other company than issuer.')),
                ('contact_type', models.IntegerField(blank=True, null=True, help_text="Leave as '----' if not primary or secondary contact.", choices=[(1, 'Primary contact'), (2, 'Secondary contact')])),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.CharField(validators=[django.core.validators.EmailValidator()], max_length=100, help_text='Eg name@host.com')),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$', message="Phone number must be entered in the format: '+999999999999'. Up to 15 digits allowed.")], max_length=17, help_text='Eg +nnnnnnnnnn')),
                ('role', models.CharField(max_length=100, help_text="Eg 'Debt analyst' or 'Legal counsel'")),
                ('date_creation', models.DateTimeField(editable=False, blank=True)),
                ('date_deletion', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical insider list',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalIssuer',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('LEI', models.CharField(db_index=True, max_length=20)),
                ('issuer_name_override', models.CharField(db_index=True, max_length=128)),
                ('description', tinymce.models.HTMLField(blank=True, null=True)),
                ('inactivated', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('gics_sub_industry', models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='static_database_table.GICSSubIndustry', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'historical issuer',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='InsiderList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(blank=True, max_length=100, null=True, help_text='If other company than issuer.')),
                ('contact_type', models.IntegerField(blank=True, null=True, help_text="Leave as '----' if not primary or secondary contact.", choices=[(1, 'Primary contact'), (2, 'Secondary contact')])),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.CharField(validators=[django.core.validators.EmailValidator()], max_length=100, help_text='Eg name@host.com')),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$', message="Phone number must be entered in the format: '+999999999999'. Up to 15 digits allowed.")], max_length=17, help_text='Eg +nnnnnnnnnn')),
                ('role', models.CharField(max_length=100, help_text="Eg 'Debt analyst' or 'Legal counsel'")),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_deletion', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Issuer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('LEI', models.CharField(max_length=20, unique=True)),
                ('issuer_name_override', models.CharField(max_length=128, unique=True)),
                ('description', tinymce.models.HTMLField(blank=True, null=True)),
                ('inactivated', models.DateTimeField(blank=True, null=True)),
                ('gics_sub_industry', models.ForeignKey(related_name='issuer_gicssubindustry_link', blank=True, to='static_database_table.GICSSubIndustry', null=True, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['issuer_name_override'],
            },
        ),
        migrations.CreateModel(
            name='IssuerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('description', models.IntegerField(unique=True, choices=[(1, 'Corporate'), (2, 'Financial institution'), (3, 'Real estate corporate')])),
            ],
        ),
        migrations.CreateModel(
            name='OnboardingProcess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enagement_letter_signed', models.BooleanField(default=False)),
                ('issuer', models.ForeignKey(related_name='onboarding_issuer_link', to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='issuer',
            name='issuer_type',
            field=models.ForeignKey(to='issuer.IssuerType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='issuer',
            name='relationship_manager',
            field=models.ForeignKey(related_name='relationship_manager_link', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='insiderlist',
            name='issuer',
            field=models.ForeignKey(related_name='insider_list_issuer_link', to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='historicalissuer',
            name='issuer_type',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issuer.IssuerType', null=True),
        ),
        migrations.AddField(
            model_name='historicalissuer',
            name='relationship_manager',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalinsiderlist',
            name='issuer',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issuer.Issuer', null=True),
        ),
        migrations.AddField(
            model_name='historicalanalyst',
            name='issuer',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to='issuer.Issuer', null=True),
        ),
        migrations.AddField(
            model_name='historicalanalyst',
            name='primary_analyst',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalanalyst',
            name='secondary_analyst',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(to='issuer.EventType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='event',
            name='issuer',
            field=models.ForeignKey(related_name='process_issuer_link', to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='event',
            name='triggered_by_user',
            field=models.ForeignKey(related_name='event_user_link', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyst',
            name='issuer',
            field=models.OneToOneField(to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyst',
            name='primary_analyst',
            field=models.ForeignKey(related_name='primary_analyst_link', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyst',
            name='secondary_analyst',
            field=models.ForeignKey(related_name='secondary_analyst_link', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
