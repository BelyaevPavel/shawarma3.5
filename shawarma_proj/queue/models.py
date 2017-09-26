# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class StaffCategory(models.Model):
    title = models.CharField(max_length=10)

    def __str__(self):
        return u"{}".format(self.title)

    def __unicode__(self):
        return u"{}".format(self.title)


class Staff(models.Model):
    staff_category = models.ForeignKey(StaffCategory)
    available = models.BooleanField(default="False")
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"{} {} {}".format(self.staff_category, self.user.first_name, self.user.last_name)

    def __unicode__(self):
        return u"{} {} {}".format(self.staff_category, self.user.first_name, self.user.last_name)


class Menu(models.Model):
    title = models.CharField(max_length=200)
    note = models.CharField(max_length=500)
    price = models.FloatField(default=0, validators=[MinValueValidator(0, "Price can't be negative!")])
    avg_preparation_time = models.DurationField(verbose_name="Average preparation time.")
    can_be_prepared_by = models.ForeignKey(StaffCategory)
    guid_1c = models.CharField(max_length=100, default="")

    def __str__(self):
        return u"{}".format(self.title)

    def __unicode__(self):
        return u"{}".format(self.title)


class Order(models.Model):
    daily_number = models.IntegerField(verbose_name="Daily Number", unique_for_date=True)
    open_time = models.DateTimeField(verbose_name="Open Time")
    close_time = models.DateTimeField(verbose_name="Close Time", null=True)
    content_completed = models.BooleanField(verbose_name="Content Completed", default=False)
    supplement_completed = models.BooleanField(verbose_name="Supplement Completed", default=False)
    total = models.FloatField(default=0, validators=[MinValueValidator(0, "Total can't be negative!")])
    is_canceled = models.BooleanField(verbose_name="Is canceled", default=False)
    closed_by = models.ForeignKey(Staff, related_name="closer", verbose_name="Closed By", null=True)
    canceled_by = models.ForeignKey(Staff, related_name="canceler", verbose_name="Canceled By", null=True)
    opened_by = models.ForeignKey(Staff, related_name="opener", verbose_name="Opened By", null=True)
    printed = models.BooleanField(default=False, verbose_name="Check Printed")
    is_paid = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('can_cancel', 'User can cancel order.'),
            ('can_close', 'User can close order.'),
        )


class OrderContent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="Menu Item")
    staff_maker = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name="Staff Maker", null=True)
    start_timestamp = models.DateTimeField(verbose_name="Start Timestamp", null=True)
    grill_timestamp = models.DateTimeField(verbose_name="Grill Start Timestamp", null=True)
    finish_timestamp = models.DateTimeField(verbose_name="Finish Timestamp", null=True)
    is_in_grill = models.BooleanField(verbose_name="Is in grill", default=False)
    is_canceled = models.BooleanField(verbose_name="Is canceled", default=False)
    canceled_by = models.ForeignKey(Staff, related_name="content_canceler", verbose_name="Canceled By", null=True)
    note = models.CharField(max_length=500, default="")

    def __str__(self):
        return u"№{} {}".format(self.order, self.menu_item)

    def __unicode__(self):
        return u"№{} {}".format(self.order, self.menu_item)

    class Meta:
        permissions = (
            ('can_cancel', 'User can cancel order content.'),
            ('can_cook', 'User can cook order content'),
        )
