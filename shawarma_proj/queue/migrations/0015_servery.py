# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-20 15:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queue', '0014_auto_20171119_1015'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500)),
                ('ip_address', models.CharField(default='', max_length=500)),
            ],
        ),
    ]
