# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Menu, Order, Staff, OrderContent
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max
import datetime
import json


# Create your views here.
@login_required()
def index(request):
    menu_items = Menu.objects.order_by('price')
    template = loader.get_template('queue/index.html')
    context = {
        'menu_items': menu_items,
    }
    return HttpResponse(template.render(context, request))


@login_required()
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


@login_required()
def production_queue(request):
    free_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                               order__close_time__isnull=True).order_by('order__open_time')
    template = loader.get_template('queue/production_queue.html')
    context = {
        'free_content': free_content
    }
    return HttpResponse(template.render(context, request))


@login_required()
@permission_required('queue.change_order')
def order_content(request, order_id):
    order_info = get_object_or_404(Order, id=order_id)
    current_order_content = OrderContent.objects.filter(order=order_id)
    template = loader.get_template('queue/order_content.html')
    context = {
        'order_info': order_info,
        'order_content': current_order_content
    }
    return HttpResponse(template.render(context, request))


@login_required()
@permission_required('queue.add_order')
def make_order(request):
    print str(request.POST['order_content'])
    content = json.loads(request.POST['order_content'])
    data = {
        'received': "Received {}".format(content)
    }
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
    for item in content:
        for i in range(0, int(item['quantity'])):
            new_order_content = OrderContent(order=order, menu_item_id=item['id'], note=item['note'])
            new_order_content.save()

    return JsonResponse(data)

@login_required()
def take(request):
    product_id = request.POST.get('id', None)
    staff_maker_id = request.POST.get('maker_id', None)
    if product_id and staff_maker_id:
        product = OrderContent.objects.get(pk=product_id)
        staff_maker = Staff.objects.get(pk=staff_maker_id)
        product.staff_maker = staff_maker
        product.start_timestamp = datetime.datetime.now()
        product.save()
    data = {
        'success': True,
        'product_id': product_id,
        'staff_maker_id': staff_maker_id
    }
    return JsonResponse(data)
