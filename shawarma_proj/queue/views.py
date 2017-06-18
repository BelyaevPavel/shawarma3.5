# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Menu, Order, Staff, OrderContent
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
import datetime


# Create your views here.
def index(request):
    menu_items = Menu.objects.order_by('price')
    template = loader.get_template('queue/index.html')
    context = {
        'menu_items': menu_items,
    }
    return HttpResponse(template.render(context, request))


def current_queue(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True).order_by(
        'open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), content_completed=True).order_by(
        'open_time')

    template = loader.get_template('queue/current_queue.html')
    context = {
        'open_orders': open_orders,
        'ready_orders': ready_orders,
        'open_length': len(open_orders),
        'ready_length': len(ready_orders)
    }
    return HttpResponse(template.render(context, request))


def order_content(request, order_id):
    orderContent = get_object_or_404(OrderContent, order=order_id)
    template = loader.get_template('queue/order_content.html')
    context = {
        'orderContent': orderContent
    }
    return HttpResponse(template.render(context, request))


def make_order(request):
    id_collection = (request.POST.get("id_collector", "")).split(',')
    del id_collection[-1]
    # order = Order(open_time=datetime.datetime.now(), daily_number=1)
    # order.save()
    order_next_number = 0
    order_last_daily_number = Order.objects.filter(open_time__contains=datetime.date.today()).aggregate(
        Max('daily_number'))
    # order_numbers = Order.objects.raw(
    #     'select id, MAX (daily_number) AS max_daily_number from queue_order where open_time >= CURRENT_DATE  GROUP BY id')
    if order_last_daily_number:
        if order_last_daily_number['daily_number__max'] is not None:
            order_next_number = order_last_daily_number['daily_number__max'] + 1
        else:
            order_next_number = 1

    order = Order(open_time=datetime.datetime.now(), daily_number=order_next_number)
    order.save()
    for ID in id_collection:
        new_order_content = OrderContent(order=order, menu_item_id=ID)
        new_order_content.save()

    return redirect('index')
