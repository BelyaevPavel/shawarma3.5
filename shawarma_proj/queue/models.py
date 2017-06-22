# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Staff(models.Model):
    name = models.CharField(max_length=100)
    StaffCategory = (('Csh', 'Cashier'), ('Ck', 'Cook'), ('Op', 'Operator'))
    category = models.CharField(max_length=3, choices=StaffCategory, default='Cashier')
    available = models.BooleanField(default="False")

    def __str__(self):
        return self.name


class Menu(models.Model):
    title = models.CharField(max_length=200)
    note = models.CharField(max_length=500)
    price = models.FloatField(default=0, validators=[MinValueValidator(0, "Price can't be negative!")])
    avg_preparation_time = models.DurationField(verbose_name="Average preparation time.")

    def __str__(self):
        return self.title


class Order(models.Model):
    daily_number = models.IntegerField(verbose_name="Daily Number", unique_for_date=True)
    open_time = models.DateTimeField(verbose_name="Open Time")
    close_time = models.DateTimeField(verbose_name="Close Time", null=True)
    content_completed = models.BooleanField(verbose_name="Content Completed", default=False)
    supplement_completed = models.BooleanField(verbose_name="Supplement Completed", default=False)
    total = models.FloatField(default=0, validators=[MinValueValidator(0, "Total can't be negative!")])
    is_canceled = models.BooleanField(verbose_name="Is canceled", default=False)


class OrderContent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="Menu Item")
    staff_maker = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name="Staff Maker", null=True)
    start_timestamp = models.DateTimeField(verbose_name="Start Timestamp", null=True)
    finish_timestamp = models.DateTimeField(verbose_name="Finish Timestamp", null=True)
    is_in_grill = models.BooleanField(verbose_name="Is in grill", default=False)
    is_canceled = models.BooleanField(verbose_name="Is canceled", default=False)
    note = models.CharField(max_length=500, default="")

    def __str__(self):
        return u"№{} {}".format(self.order, self.menu_item)
