# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import methodology.models
import config.storage_backends
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Methodology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date_decision', models.DateTimeField()),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('upload', models.FileField(upload_to=methodology.models.get_upload_to, storage=config.storage_backends.AnalyticalMediaStorage())),
            ],
            options={
                'ordering': ('category', '-date_decision'),
            },
        ),
        migrations.CreateModel(
            name='MethodologyCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='methodology',
            name='category',
            field=models.ForeignKey(related_name='methodology_methodology_category', to='methodology.MethodologyCategory', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='methodology',
            name='uploaded_by',
            field=models.ForeignKey(related_name='methodology_methodology_user', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
