# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-02-11 05:09


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shaw_queue', '0022_orderopinion'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderopinion',
            name='post_time',
            field=models.DateTimeField(null=True, verbose_name='Post Time'),
        ),
    ]
