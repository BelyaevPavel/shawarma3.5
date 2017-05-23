# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Menu, Staff, Order
from django.contrib import admin

# Register your models here.
admin.site.register(Menu)
admin.site.register(Staff)
admin.site.register(Order)