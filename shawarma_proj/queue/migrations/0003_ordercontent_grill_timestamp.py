# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-11 06:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queue', '0002_auto_20170705_0543'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordercontent',
            name='grill_timestamp',
            field=models.DateTimeField(null=True, verbose_name='Grill Start Timestamp'),
        ),
    ]
