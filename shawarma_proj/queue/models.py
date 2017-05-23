# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Staff(models.Model):
    name = models.CharField(max_length=100)
    StaffCategory = (('Csh', 'Cashier'), ('Ck', 'Cook'), ('Op', 'Operator'))
    category = models.CharField(max_length=3, choices=StaffCategory, default='Cashier')

    def __str__(self):
        return self.name


class Menu(models.Model):
    title = models.CharField(max_length=200)
    note = models.CharField(max_length=500)
    avg_preparation_time = models.DurationField(verbose_name="Average preparation time.")

    def __str__(self):
        return self.title


class Order(models.Model):
    daily_number = models.IntegerField(verbose_name="Daily Number")
    open_time = models.DateTimeField(verbose_name="Open Time")
    close_time = models.DateTimeField(verbose_name="Close Time")
    content_completed = models.BooleanField(verbose_name="Content Completed")
    supplement_completed = models.BooleanField(verbose_name="Supplement Completed")


class OrderContent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="Menu Item")
    staff_maker = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name="Staff Maker")
    start_timestamp = models.DateTimeField(verbose_name="Start Timestamp")
    finish_timestamp = models.DateTimeField(verbose_name="Finish Timestamp")
