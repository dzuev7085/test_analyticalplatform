# Generated by Django 2.1.3 on 2018-11-22 13:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating_process', '0009_issuedecisionattribute_is_matured'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='internalscoredata',
            options={'ordering': ['rating_decision__issuer', 'rating_decision', 'subfactor__factor', 'subfactor']},
        ),
        migrations.AlterField(
            model_name='historicalinternalscoredata',
            name='decided_score',
            field=models.IntegerField(blank=True, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-'), (None, 'n/a')], default=False, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)]),
        ),
        migrations.AlterField(
            model_name='historicalinternalscoredata',
            name='proposed_score',
            field=models.IntegerField(blank=True, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-'), (None, 'n/a')], default=False, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)]),
        ),
        migrations.AlterField(
            model_name='internalscoredata',
            name='decided_score',
            field=models.IntegerField(blank=True, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-'), (None, 'n/a')], default=False, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)]),
        ),
        migrations.AlterField(
            model_name='internalscoredata',
            name='proposed_score',
            field=models.IntegerField(blank=True, choices=[(1, 'aa'), (2, 'aa-'), (3, 'a+'), (4, 'a'), (5, 'a-'), (6, 'bbb+'), (7, 'bbb'), (8, 'bbb-'), (9, 'bb+'), (10, 'bb'), (11, 'bb-'), (12, 'b+'), (13, 'b'), (14, 'b-'), (None, 'n/a')], default=False, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(14)]),
        ),
    ]
