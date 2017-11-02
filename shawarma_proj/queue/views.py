# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Menu, Order, Staff, StaffCategory, OrderContent
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, Count, Avg, F
from hashlib import md5
from shawarma.settings import TIME_ZONE, LISTNER_URL
import requests
import datetime
import json


@login_required()
def redirection(request):
    staff_category = StaffCategory.objects.get(staff__user=request.user)
    if staff_category.title == 'Cook':
        return HttpResponseRedirect('cook_interface')
    if staff_category.title == 'Cashier':
        return HttpResponseRedirect('menu')
    if staff_category.title == 'Operator':
        return HttpResponseRedirect('current_queue')


# Create your views here.
@login_required()
def welcomer(request):
    template = loader.get_template('queue/welcomer.html')
    context = {
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def menu(request):
    menu_items = Menu.objects.order_by('price')
    template = loader.get_template('queue/menu_page.html')
    context = {
        'user': request.user,
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
        'menu_items': menu_items,
    }
    return HttpResponse(template.render(context, request))


def buyer_queue(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       supplement_completed=False, is_canceled=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        content_completed=True, supplement_completed=True, is_canceled=False).order_by(
        'open_time')
    context = {
        'open_orders': open_orders,
        'ready_orders': ready_orders
    }
    template = loader.get_template('queue/buyer_queue.html')
    return HttpResponse(template.render(context, request))


def buyer_queue_ajax(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       supplement_completed=False, is_canceled=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        content_completed=True, supplement_completed=True, is_canceled=False).order_by(
        'open_time')
    context = {
        'open_orders': open_orders,
        'ready_orders': ready_orders
    }
    template = loader.get_template('queue/buyer_queue_ajax.html')
    data = {
        'html': template.render(context, request),
        'ready': json.dumps([order.daily_number for order in ready_orders])
    }
    return JsonResponse(data)


@login_required()
def current_queue(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       is_canceled=False, supplement_completed=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        is_canceled=False, content_completed=True, supplement_completed=True).order_by(
        'open_time')

    template = loader.get_template('queue/current_queue_grid.html')
    context = {
        'open_orders': [{'order': open_order,
                         'printed': open_order.printed,
                         'cook_part_ready_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').filter(
                             finish_timestamp__isnull=False).aggregate(count=Count('id')),
                         'cook_part_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').aggregate(count=Count('id')),
                         'operator_part': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='operator')
                         } for open_order in open_orders],
        'ready_orders': [{'order': open_order,
                          'cook_part_ready_count': OrderContent.objects.filter(order=open_order).filter(
                              menu_item__can_be_prepared_by__title__iexact='cook').filter(
                              finish_timestamp__isnull=False).aggregate(count=Count('id')),
                          'cook_part_count': OrderContent.objects.filter(order=open_order).filter(
                              menu_item__can_be_prepared_by__title__iexact='cook').aggregate(count=Count('id')),
                          'operator_part': OrderContent.objects.filter(order=open_order).filter(
                              menu_item__can_be_prepared_by__title__iexact='operator')
                          } for open_order in ready_orders],
        'open_length': len(open_orders),
        'ready_length': len(ready_orders),
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
    }
    return HttpResponse(template.render(context, request))


@login_required()
def current_queue_ajax(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       is_canceled=False, supplement_completed=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        is_canceled=False, content_completed=True, supplement_completed=True).order_by(
        'open_time')

    template = loader.get_template('queue/current_queue_grid_ajax.html')
    context = {
        'open_orders': [{'order': open_order,
                         'printed': open_order.printed,
                         'cook_part_ready_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').filter(
                             finish_timestamp__isnull=False).aggregate(count=Count('id')),
                         'cook_part_count': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='cook').aggregate(count=Count('id')),
                         'operator_part': OrderContent.objects.filter(order=open_order).filter(
                             menu_item__can_be_prepared_by__title__iexact='operator')
                         } for open_order in open_orders],
        'ready_orders': [{'order': open_order,
                          'cook_part_ready_count': OrderContent.objects.filter(order=open_order).filter(
                              menu_item__can_be_prepared_by__title__iexact='cook').filter(
                              finish_timestamp__isnull=False).aggregate(count=Count('id')),
                          'cook_part_count': OrderContent.objects.filter(order=open_order).filter(
                              menu_item__can_be_prepared_by__title__iexact='cook').aggregate(count=Count('id')),
                          'operator_part': OrderContent.objects.filter(order=open_order).filter(
                              menu_item__can_be_prepared_by__title__iexact='operator')
                          } for open_order in ready_orders],
        'open_length': len(open_orders),
        'ready_length': len(ready_orders),
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
    }
    data = {
        'html': template.render(context, request)
    }
    return JsonResponse(data)


@login_required()
def production_queue(request):
    free_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                               order__close_time__isnull=True,
                                               menu_item__can_be_prepared_by__title__iexact='cook',
                                               finish_timestamp__isnull=True).order_by(
        'order__open_time')
    template = loader.get_template('queue/production_queue.html')
    context = {
        'free_content': free_content,
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
    }
    return HttpResponse(template.render(context, request))


def cook_interface(request):
    def new_processor(request):
        user = request.user
        context = None
        order_content = None
        taken_orders = Order.objects.filter(prepared_by__user=user, open_time__isnull=False,
                                            close_time__isnull=True)
        has_order = False
        if len(taken_orders) > 0:
            has_order = True

        if not has_order:
            free_orders = Order.objects.filter(prepared_by=None).order_by('open_time')

            if len(free_orders) > 0:
                free_order = free_orders[0]
                free_order.prepared_by.user = user
                order_content = OrderContent.objects.filter(order=free_order)
                context = {
                    'free_order': free_order,
                    'order_content': order_content
                }
        else:
            order_content = OrderContent.objects.filter(order=taken_orders[0])
            context = {
                'free_order': taken_orders,
                'order_content': order_content
            }

        template = loader.get_template('queue/cook_interface_alt.html')
        return HttpResponse(template.render(context, request))

    def old_processor(request):
        user = request.user
        user_avg_prep_duration = OrderContent.objects.filter(staff_maker__user=user, start_timestamp__isnull=False,
                                                             finish_timestamp__isnull=False).values(
            'menu_item__id').annotate(
            production_duration=Avg(F('finish_timestamp') - F('start_timestamp'))).order_by('production_duration')

        available_cook_count = Staff.objects.filter(user__last_login__contains=datetime.date.today(),
                                                    staff_category__title__iexact='cook').aggregate(
            Count('id'))  # Change to logged.

        free_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                                   order__close_time__isnull=True,
                                                   order__is_canceled=False,
                                                   menu_item__can_be_prepared_by__title__iexact='cook',
                                                   start_timestamp__isnull=True).order_by(
            'order__open_time')[:available_cook_count['id__count']]

        in_progress_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                                          order__close_time__isnull=True,
                                                          order__is_canceled=False,
                                                          start_timestamp__isnull=False,
                                                          finish_timestamp__isnull=True,
                                                          staff_maker__user=user,
                                                          is_in_grill=False,
                                                          is_canceled=False).order_by(
            'order__open_time')[:1]

        in_grill_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                                       order__close_time__isnull=True,
                                                       order__is_canceled=False,
                                                       start_timestamp__isnull=False,
                                                       finish_timestamp__isnull=True,
                                                       staff_maker__user=user,
                                                       is_in_grill=True,
                                                       is_canceled=False)

        in_grill_dict = [{'product': product,
                          'time_in_grill': datetime.datetime.now().replace(tzinfo=None) - product.grill_timestamp.replace(
                              tzinfo=None)} for product in in_grill_content]

        if len(free_content) > 0:
            if len(in_progress_content) == 0:
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
                    'in_progress': None,
                    'in_grill': in_grill_dict,
                    'current_time': datetime.datetime.now(),
                    'staff_category': StaffCategory.objects.get(staff__user=request.user),
                }
            else:
                context = {
                    'next_product': None,
                    'in_progress': in_progress_content[0],
                    'in_grill': in_grill_dict,
                    'current_time': datetime.datetime.now(),
                    'staff_category': StaffCategory.objects.get(staff__user=request.user),
                }
        else:
            if len(in_progress_content) != 0:
                context = {
                    'next_product': None,
                    'in_progress': in_progress_content[0],
                    'in_grill': in_grill_dict,
                    'current_time': datetime.datetime.now(),
                    'staff_category': StaffCategory.objects.get(staff__user=request.user),

                }
            else:
                context = {
                    'next_product': None,
                    'in_progress': None,
                    'in_grill': in_grill_dict,
                    'current_time': datetime.datetime.now(),
                    'staff_category': StaffCategory.objects.get(staff__user=request.user),

                }

        template = loader.get_template('queue/cook_interface.html')
        return HttpResponse(template.render(context, request))

    return new_processor(request)


@login_required()
@permission_required('queue.change_order')
def set_cooker(request, order_id, cooker_id):
    order = Order.objects.get_object_or_404(id=order_id)
    cooker = Staff.objects.get_object_or_404(id=cooker_id)
    order.prepared_by = cooker

    return JsonResponse(data={'success': True})


@login_required()
@permission_required('queue.change_order')
def order_content(request, order_id):
    order_info = get_object_or_404(Order, id=order_id)
    order_content = OrderContent.objects.filter(order_id=order_id)
    flag = True
    for item in order_content:
        if item.finish_timestamp is None:
            flag = False
    if flag:
        order_info.content_completed = True
        order_info.supplement_completed = True
    order_info.save()
    current_order_content = OrderContent.objects.filter(order=order_id)
    template = loader.get_template('queue/order_content.html')
    context = {
        'order_info': order_info,
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
        'order_content': current_order_content,
        'ready': order_info.content_completed and order_info.supplement_completed
    }
    return HttpResponse(template.render(context, request))


def print_order(request, order_id):
    order_info = get_object_or_404(Order, id=order_id)
    order_info.printed = True
    order_info.save()
    order_content = OrderContent.objects.filter(order_id=order_id).values('menu_item__title',
                                                                          'menu_item__price').annotate(
        count=Count('menu_item__title'))
    template = loader.get_template('queue/print_order.html')
    context = {
        'order_info': order_info,
        'order_content': order_content
    }
    return HttpResponse(template.render(context, request))


@login_required()
@permission_required('queue.add_order')
def make_order(request):
    content = json.loads(request.POST['order_content'])
    is_paid = json.loads(request.POST['is_paid'])
    paid_with_cash = json.loads(request.POST['paid_with_cash'])
    order_next_number = 0
    order_last_daily_number = Order.objects.filter(open_time__contains=datetime.date.today()).aggregate(
        Max('daily_number'))
    if order_last_daily_number:
        if order_last_daily_number['daily_number__max'] is not None:
            order_next_number = order_last_daily_number['daily_number__max'] + 1
        else:
            order_next_number = 1

    order = Order(open_time=datetime.datetime.now(), daily_number=order_next_number, is_paid=is_paid,
                  paid_with_cash=paid_with_cash)
    order.save()
    data = {
        "daily_number": order.daily_number
    }
    content_to_send = []

    total = 0
    for item in content:
        for i in range(0, int(item['quantity'])):
            new_order_content = OrderContent(order=order, menu_item_id=item['id'], note=item['note'])
            new_order_content.save()
            menu_item = Menu.objects.get(id=item['id'])
            total += menu_item.price

        content_to_send.append(
            {
                'item_id': item['id'],
                'quantity': item['quantity']
            }
        )

    order.total = total
    order.save()
    prepare_json_check(order)
    #if order.is_paid:
    #    requests.post(LISTNER_URL, json=prepare_json_check(order))
    data["total"] = order.total
    data["content"] = json.dumps(content_to_send)
    return JsonResponse(data)


@login_required()
@permission_required('queue.change_order')
def close_order(request):
    order_id = json.loads(request.POST.get('order_id', None))
    order = Order.objects.get(id=order_id)
    order.close_time = datetime.datetime.now()
    order.save()
    data = {
        'success': True,
        'received': u'Order №{} is closed.'.format(order.daily_number)
    }

    return JsonResponse(data)


@login_required()
@permission_required('queue.change_order')
def cancel_order(request):
    order_id = request.POST.get('id', None)
    if order_id:
        order = Order.objects.get(id=order_id)
        order.canceled_by = Staff.objects.get(user=request.user)
        order.is_canceled = True
        order.save()
        data = {
            'success': True
        }
    else:
        data = {
            'success': False
        }

    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def next_to_prepare(request):
    user = request.user
    user_avg_prep_duration = OrderContent.objects.filter(staff_maker__user=user, start_timestamp__isnull=False,
                                                         finish_timestamp__isnull=False).values(
        'menu_item__id').annotate(
        production_duration=Avg(F('finish_timestamp') - F('start_timestamp'))).order_by('production_duration')

    available_cook_count = Staff.objects.filter(user__last_login__contains=datetime.date.today(),
                                                staff_category__title__iexact='cook').aggregate(
        Count('id'))  # Change to logged.

    free_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                               order__close_time__isnull=True,
                                               order__is_canceled=False,
                                               menu_item__can_be_prepared_by__title__iexact='cook',
                                               start_timestamp__isnull=True).order_by(
        'order__open_time')[:available_cook_count['id__count']]

    in_progress_content = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                                      order__close_time__isnull=True,
                                                      order__is_canceled=False,
                                                      start_timestamp__isnull=False,
                                                      finish_timestamp__isnull=True,
                                                      staff_maker__user=user,
                                                      is_in_grill=False,
                                                      is_canceled=False).order_by(
        'order__open_time')[:1]

    if len(free_content) > 0:
        if len(in_progress_content) == 0:
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
                'in_progress': None,
                'current_time': datetime.datetime.now(),
                'staff_category': StaffCategory.objects.get(staff__user=request.user),
            }
        else:
            context = {
                'next_product': None,
                'in_progress': in_progress_content[0],
                'current_time': datetime.datetime.now(),
                'staff_category': StaffCategory.objects.get(staff__user=request.user),
            }
    else:
        if len(in_progress_content) != 0:
            context = {
                'next_product': None,
                'in_progress': in_progress_content[0],
                'current_time': datetime.datetime.now(),
                'staff_category': StaffCategory.objects.get(staff__user=request.user),

            }
        else:
            context = {
                'next_product': None,
                'in_progress': None,
                'current_time': datetime.datetime.now(),
                'staff_category': StaffCategory.objects.get(staff__user=request.user),
            }

    template = loader.get_template('queue/next_to_prepare_ajax.html')
    data = {
        'html': template.render(context, request)
    }
    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def take(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(id=product_id)
        if product.staff_maker is None:
            staff_maker = Staff.objects.get(user=request.user)
            product.staff_maker = staff_maker
            product.start_timestamp = datetime.datetime.now()
            product.save()

            data = {
                'success': True
            }
        else:
            data = {
                'success': False,
                'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
            }

    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def to_grill(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(pk=product_id)
        product.grill_timestamp = datetime.datetime.now()
        product.is_in_grill = True
        product.save()
    data = {
        'success': True,
        'product_id': product_id,
        'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
    }

    return JsonResponse(data)


@login_required()
def grill_timer(request):
    grilling = OrderContent.objects.filter(order__open_time__contains=datetime.date.today(),
                                           order__close_time__isnull=True,
                                           order__is_canceled=False,
                                           start_timestamp__isnull=False,
                                           finish_timestamp__isnull=True,
                                           staff_maker__user=request.user,
                                           is_in_grill=True,
                                           is_canceled=False)
    template = loader.get_template('queue/grill_slot_ajax.html')
    tzinfo = datetime.tzinfo(tzname=TIME_ZONE)
    context = {
        'in_grill': [{'time': str(datetime.datetime.now().replace(tzinfo=tzinfo) - product.grill_timestamp.replace(
            tzinfo=tzinfo))[:-str(datetime.datetime.now().replace(tzinfo=tzinfo) - product.grill_timestamp.replace(
            tzinfo=tzinfo)).find('.')],
                      'product': product} for product in grilling]
    }
    data = {
        'html': template.render(context, request)
    }
    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def finish_cooking(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(pk=product_id)
        product.is_in_grill = False
        product.finish_timestamp = datetime.datetime.now()
        product.save()
        order_content = OrderContent.objects.filter(order_id=product.order_id)
        flag = True
        for item in order_content:
            if item.finish_timestamp is None:
                flag = False
        if flag:
            product.order.content_completed = True
            product.order.supplement_completed = True
        data = {
            'success': True,
            'product_id': product_id,
            'order_number': product.order.daily_number,
            'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
        }
    else:
        data = {
            'success': False,
            'product_id': product_id,
            'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
        }

    return JsonResponse(data)


@login_required()
@permission_required('queue.can_cook')
def finish_supplement(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(id=product_id)
        product.start_timestamp = datetime.datetime.now()
        product.finish_timestamp = datetime.datetime.now()
        product.staff_maker = Staff.objects.get(user=request.user)
        product.save()
        order_content = OrderContent.objects.filter(order_id=product.order_id)
        flag = True
        for item in order_content:
            if item.finish_timestamp is None:
                flag = False
        if flag:
            product.order.content_completed = True
            product.order.supplement_completed = True
        data = {
            'success': True,
            'product_id': product_id,
            'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
        }
    else:
        data = {
            'success': False,
            'product_id': product_id,
            'staff_maker': u'{} {}'.format(request.user.first_name, request.user.last_name)
        }

    return JsonResponse(data)


@login_required()
@permission_required('queue.change_order')
def ready_order(request):
    order_id = request.POST.get('id', None)
    if order_id:
        order = Order.objects.get(id=order_id)
        order.save()
        data = {
            'success': True
        }
    else:
        data = {
            'success': False
        }

    return JsonResponse(data)


@login_required()
@permission_required('queue.change_order')
def cancel_item(request):
    product_id = request.POST.get('id', None)
    if product_id:
        item = OrderContent.objects.get(id=product_id)
        item.canceled_by = request.user
        item.is_canceled = True
        item.save()
        data = {
            'success': True
        }
    else:
        data = {
            'success': False
        }

    return JsonResponse(data)


@login_required()
def statistic_page(request):
    template = loader.get_template('queue/statistics.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


def prepare_json_check(order):
    aux_query = OrderContent.objects.filter(order=order).values('menu_item__title', 'menu_item__guid_1c',
                                                                'menu_item__price', 'order__paid_with_cash').annotate(
        total=Count('menu_item__title'))
    rows = []
    number = 1
    sum = 0
    payment_type_uid = ""
    if aux_query[0]['order__paid_with_cash']:
        payment_type_uid = "5715e4bd-767b-11e6-82c6-28c2dd30392b"
    else:
        payment_type_uid = ""
    for item in aux_query:
        rows.append({
            u"НомерСтроки": number,
            u"КлючСвязи": number,
            u"Количество": item['total'],
            u"КоличествоУпаковок": item['total'],
            u"НеобходимостьВводаАкцизнойМарки": False,
            u"Номенклатура": {
                "TYPE": "СправочникСсылка.Номенклатура",
                "UID": item['menu_item__guid_1c']
            },
            u"ПродажаПодарка": False,
            u"РегистрацияПродажи": False,
            u"Резервировать": False,
            u"Склад": {
                "TYPE": "СправочникСсылка.Склады",
                "UID": "cc442ddc-767b-11e6-82c6-28c2dd30392b"
            },
            "СтавкаНДС": {
                "TYPE": "ПеречислениеСсылка.СтавкиНДС",
                "UID": "БезНДС"
            },
            "Сумма": item['menu_item__price'] * item['total'],
            "Цена": item['menu_item__price']
        })
        number += 1
        sum += item['menu_item__price'] * item['total']
    aux_dict = {
        "OBJECT": True,
        "NEW": "Документы.ЧекККМ.СоздатьДокумент()",
        "SAVE": True,
        "Проведен": True,
        "Ссылка": {
            "TYPE": "ДокументСсылка.ЧекККМ",
            "UID": "0000-0000-0000-0000-0000"
        },
        "ПометкаУдаления": False,
        "Дата": {
            "TYPE": "Дата",
            "UID": None
        },
        "Номер": "0000-ЯЯЯЯЯЯ",
        "АналитикаХозяйственнойОперации": {
            "TYPE": "СправочникСсылка.АналитикаХозяйственныхОпераций",
            "UID": "5715e4c9-767b-11e6-82c6-28c2dd30392b"
        },
        "БонусыНачислены": False,
        "ВидОперации": {
            "TYPE": "ПеречислениеСсылка.ВидыОперацийЧекККМ",
            "UID": "Продажа"
        },
        "ДисконтнаяКарта": {
            "TYPE": "СправочникСсылка.ИнформационныеКарты",
            "UID": "7ba5d64b-e6b0-11e6-8279-002215bf2d6a"
        },
        "КассаККМ": {
            "TYPE": "СправочникСсылка.КассыККМ",
            "UID": "8414dfc5-7683-11e6-8251-002215bf2d6a"
        },
        "Магазин": {
            "TYPE": "СправочникСсылка.Магазины",
            "UID": "cc442ddb-767b-11e6-82c6-28c2dd30392b"
        },
        "НомерЧекаККМ": 6036,
        "Организация": {
            "TYPE": "СправочникСсылка.Организации",
            "UID": "1d68a28e-767b-11e6-82c6-28c2dd30392b"
        },
        "Ответственный": {
            "TYPE": "СправочникСсылка.Пользователи",
            "UID": "1d68a28d-767b-11e6-82c6-28c2dd30392b"
        },
        "ОтработанПереход": False,
        "ОтчетОРозничныхПродажах": {
            "TYPE": "ДокументСсылка.ОтчетОРозничныхПродажах",
            "UID": "1f1b7ecd-8760-11e7-82a6-002215bf2d6a"
        },
        "СкидкиРассчитаны": True,
        "СтатусЧекаККМ": {
            "TYPE": "ПеречислениеСсылка.СтатусыЧековККМ",
            "UID": "Архивный"
        },
        "СуммаДокумента": sum,
        "ЦенаВключаетНДС": False,
        "ОперацияСДенежнымиСредствами": False,
        "Товары": {
            "TYPE": "ТаблицаЗначений",
            "COLUMNS": {
                "НомерСтроки": None,
                "ЗаказПокупателя": None,
                "КлючСвязи": None,
                "КлючСвязиСерийныхНомеров": None,
                "КодСтроки": None,
                "Количество": None,
                "КоличествоУпаковок": None,
                "НеобходимостьВводаАкцизнойМарки": None,
                "Номенклатура": None,
                "Продавец": None,
                "ПродажаПодарка": None,
                "ПроцентАвтоматическойСкидки": None,
                "ПроцентРучнойСкидки": None,
                "РегистрацияПродажи": None,
                "Резервировать": None,
                "Склад": None,
                "СтавкаНДС": None,
                "СтатусУказанияСерий": None,
                "Сумма": None,
                "СуммаАвтоматическойСкидки": None,
                "СуммаНДС": None,
                "СуммаРучнойСкидки": None,
                "СуммаСкидкиОплатыБонусом": None,
                "Упаковка": None,
                "Характеристика": None,
                "Цена": None,
                "Штрихкод": None
            },
            "ROWS": rows
        },
        "Оплата": {
            "TYPE": "ТаблицаЗначений",
            "COLUMNS": {
                "НомерСтроки": None,
                "ВидОплаты": None,
                "ЭквайринговыйТерминал": None,
                "Сумма": None,
                "ПроцентКомиссии": None,
                "СуммаКомиссии": None,
                "СсылочныйНомер": None,
                "НомерЧекаЭТ": None,
                "НомерПлатежнойКарты": None,
                "ДанныеПереданыВБанк": None,
                "СуммаБонусовВСкидках": None,
                "КоличествоБонусов": None,
                "КоличествоБонусовВСкидках": None,
                "БонуснаяПрограммаЛояльности": None,
                "ДоговорПлатежногоАгента": None,
                "КлючСвязиОплаты": None
            },
            "ROWS": [
                {
                    "НомерСтроки": 1,
                    "ВидОплаты": {
                        "TYPE": "СправочникСсылка.ВидыОплатЧекаККМ",
                        "UID": payment_type_uid
                    },
                    "Сумма": sum,
                    "ДанныеПереданыВБанк": False
                }
            ]
        }
    }
    print json.dumps(aux_dict)
    return json.dumps(aux_dict)
