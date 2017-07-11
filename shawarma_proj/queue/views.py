# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Menu, Order, Staff, OrderContent
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, Count, Avg, F
from hashlib import md5
import datetime
import json


# Create your views here.
@login_required()
def menu(request):
    menu_items = Menu.objects.order_by('price')
    template = loader.get_template('queue/menu_page.html')
    context = {
        'user': request.user,
        'menu_items': menu_items,
    }
    return HttpResponse(template.render(context, request))


@login_required()
def current_queue(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True).order_by(
        'open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), content_completed=True).order_by(
        'open_time')

    template = loader.get_template('queue/current_queue_grid.html')
    context = {
        'open_orders': [{'order': open_order,
                         'cook_part_ready_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').filter(
                             finish_timestamp__isnull=False).aggregate(count=Count('id')),
                         'cook_part_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').aggregate(count=Count('id')),
                         'operator_part': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='operator')
                         } for open_order in open_orders],
        'ready_orders': ready_orders,
        'open_length': len(open_orders),
        'ready_length': len(ready_orders)
    }
    return HttpResponse(template.render(context, request))


@login_required()
def current_queue_ajax(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True).order_by(
        'open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), content_completed=True).order_by(
        'open_time')

    template = loader.get_template('queue/current_queue_grid_ajax.html')
    context = {
        'open_orders': [{'order': open_order,
                         'cook_part_ready_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').filter(
                             finish_timestamp__isnull=False).aggregate(count=Count('id')),
                         'cook_part_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').aggregate(count=Count('id')),
                         'operator_part': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='operator')
                         } for open_order in open_orders],
        'ready_orders': ready_orders,
        'open_length': len(open_orders),
        'ready_length': len(ready_orders)
    }
    return HttpResponse(template.render(context, request))


@login_required()
def production_queue(request):
    free_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                               order__close_time__isnull=True,
                                               menu_item__can_be_prepared_by__title__iexact='cook',
                                               finish_timestamp__isnull=True).order_by(
        'order__open_time')
    template = loader.get_template('queue/production_queue.html')
    context = {
        'free_content': free_content
    }
    return HttpResponse(template.render(context, request))


def cook_interface(request):
    user = request.user
    user_avg_prep_duration = OrderContent.objects.filter(staff_maker__user=user, start_timestamp__isnull=False,
                                                         finish_timestamp__isnull=False).values(
        'menu_item__id').annotate(
        production_duration=Avg(F('finish_timestamp') - F('start_timestamp'))).order_by('production_duration')
    print user_avg_prep_duration
    available_cook_count = Staff.objects.filter(available=True, staff_category__title__iexact='cook').aggregate(
        Count('id'))  # Change to logged.
    print available_cook_count['id__count']
    free_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                               order__close_time__isnull=True,
                                               menu_item__can_be_prepared_by__title__iexact='cook',
                                               start_timestamp__isnull=True).order_by(
        'order__open_time')[:available_cook_count['id__count']]
    print free_content
    in_progress_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                                      order__close_time__isnull=True,
                                                      start_timestamp__isnull=False,
                                                      finish_timestamp__isnull=True,
                                                      staff_maker__user=user,
                                                      is_in_grill=False,
                                                      is_canceled=False).order_by(
        'order__open_time')[:1]
    print in_progress_content
    if len(free_content) > 0 and len(in_progress_content) == 0:
        free_content_ids = [content.id for content in free_content]
        id_to_prepare = -1
        for product in user_avg_prep_duration:
            if product['menu_item__id'] in free_content_ids:
                id_to_prepare = product['menu_item__id']
                break

        if id_to_prepare == -1:
            id_to_prepare = free_content_ids[0]

        context = {
            'next_product': OrderContent.objects.get(id=id_to_prepare),
            'in_progress': None
        }

    else:
        context = {
            'next_product': None,
            'in_progress': in_progress_content[0]
        }

    template = loader.get_template('queue/cook_interface.html')

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
    content = json.loads(request.POST['order_content'])
    data = {
        'received': "Received {}".format(content)
    }
    order_next_number = 0
    order_last_daily_number = Order.objects.filter(open_time__contains=datetime.date.today()).aggregate(
        Max('daily_number'))
    if order_last_daily_number:
        if order_last_daily_number['daily_number__max'] is not None:
            order_next_number = order_last_daily_number['daily_number__max'] + 1
        else:
            order_next_number = 1

    order = Order(open_time=datetime.datetime.now(), daily_number=order_next_number)
    order.save()
    total = 0
    for item in content:
        for i in range(0, int(item['quantity'])):
            new_order_content = OrderContent(order=order, menu_item_id=item['id'], note=item['note'])
            new_order_content.save()
            menu_item = Menu.objects.get(id=item['id'])
            total += menu_item.price

    order.total = total
    order.save()

    return JsonResponse(data)


@login_required()
@permission_required('queue.change_order')
def close_order(request):
    content = json.loads(request.POST['order_id'])
    order = Order.objects.get(id=content)
    order.close_time = datetime.datetime.now()
    order.save()
    data = {
        'received': u'Order №{} is closed.'.format()
    }

    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def take(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(pk=product_id)
        staff_maker = Staff.objects.get(user=request.user)
        product.staff_maker = staff_maker
        product.start_timestamp = datetime.datetime.now()
        product.save()
    data = {
        'success': True,
        'product_id': product_id,
        'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
    }

    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def to_grill(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(pk=product_id)
        product.is_in_grill = True
        product.save()
    data = {
        'success': True,
        'product_id': product_id,
        'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
    }

    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def finish_cooking(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(pk=product_id)
        product.finish_timestamp = datetime.datetime.now()
        product.save()
    data = {
        'success': True,
        'product_id': product_id,
        'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
    }

    return JsonResponse(data)
