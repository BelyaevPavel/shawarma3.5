# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-21 05:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queue', '0020_order_is_grilling_shash'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shashlyk_completed',
            field=models.BooleanField(default=False, verbose_name='Shashlyk Completed'),
        ),
        migrations.AlterField(
            model_name='order',
            name='is_grilling_shash',
            field=models.BooleanField(default=False, verbose_name='Shashlyk Is Grilling'),
        ),
    ]
