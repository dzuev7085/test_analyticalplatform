# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PressRelease',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('header', models.CharField(blank=True, null=True, max_length=255, help_text='A short but informative head line.')),
                ('pre_amble', tinymce.models.HTMLField(blank=True, help_text='An introduction to the body. This is often the only part included by media so keep the text crispy.', null=True)),
                ('body', tinymce.models.HTMLField(blank=True, help_text='The rest of the press release.', null=True)),
                ('rating_decision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rating_process.RatingDecision')),
            ],
        ),
    ]
