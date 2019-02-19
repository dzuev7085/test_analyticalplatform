# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import upload.models
import django.db.models.deletion
import config.storage_backends
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0001_initial'),
        ('issuer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticalDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_value', models.DateTimeField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('upload', models.FileField(upload_to=upload.models.get_upload_to, storage=config.storage_backends.AnalyticalMediaStorage())),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SecurityClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='analyticaldocument',
            name='document_type',
            field=models.ForeignKey(related_name='upload_analytical_document_document_type', to='upload.DocumentType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyticaldocument',
            name='issuer',
            field=models.ForeignKey(related_name='upload_analytical_document', to='issuer.Issuer', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyticaldocument',
            name='rating_decision',
            field=models.ForeignKey(to='rating_process.RatingDecision', blank=True, null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyticaldocument',
            name='security_class',
            field=models.ForeignKey(related_name='upload_analytical_document_security_class', default=4, to='upload.SecurityClass', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='analyticaldocument',
            name='uploaded_by',
            field=models.ForeignKey(related_name='upload_analytical_document_user', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
