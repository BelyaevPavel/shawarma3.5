# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponseRedirect

from .models import Menu, Order, Staff, StaffCategory, MenuCategory, OrderContent, Servery
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, login, views as auth_views
from django.db.models import Max, Count, Avg, F
from hashlib import md5
from shawarma.settings import TIME_ZONE, LISTNER_URL, LISTNER_PORT, PRINTER_URL
import requests
import datetime
import json
import os
import subprocess


@login_required()
def redirection(request):
    staff_category = StaffCategory.objects.get(staff__user=request.user)
    if staff_category.title == 'Cook':
        return HttpResponseRedirect('cook_interface')
    if staff_category.title == 'Cashier':
        return HttpResponseRedirect('menu')
    if staff_category.title == 'Operator':
        return HttpResponseRedirect('current_queue')


def logout_view(request):
    user = request.user
    staff = Staff.objects.get(user=user)
    if staff.available:
        staff.available = False
        staff.save()
    logout(request)
    return redirect('welcomer')


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
    menu_items = Menu.objects.order_by('title')
    template = loader.get_template('queue/menu_page.html')
    context = {
        'user': request.user,
        'available_cookers': Staff.objects.filter(user__last_login__contains=datetime.date.today(), available=True,
                                                  staff_category__title__iexact='Cook'),
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
        'menu_items': menu_items,
        'menu_categories': MenuCategory.objects.order_by('weight')
    }
    return HttpResponse(template.render(context, request))


def buyer_queue(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       is_canceled=False, is_ready=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        content_completed=True, supplement_completed=True, is_ready=True,
                                        is_canceled=False).order_by('open_time')
    context = {
        'open_orders': [{'servery': order.servery, 'daily_number': order.daily_number % 1000} for order in open_orders],
        'ready_orders': [{'servery': order.servery, 'daily_number': order.daily_number % 1000} for order in
                         ready_orders]
    }
    template = loader.get_template('queue/buyer_queue.html')
    return HttpResponse(template.render(context, request))


def buyer_queue_ajax(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       is_canceled=False, is_ready=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        content_completed=True, supplement_completed=True, is_ready=True,
                                        is_canceled=False).order_by('open_time')
    context = {
        'open_orders': [{'servery': order.servery, 'daily_number': order.daily_number % 1000} for order in open_orders],
        'ready_orders': [{'servery': order.servery, 'daily_number': order.daily_number % 1000} for order in
                         ready_orders]
    }
    template = loader.get_template('queue/buyer_queue_ajax.html')
    data = {
        'html': template.render(context, request),
        'ready': json.dumps([order.daily_number for order in ready_orders]),
        'voiced': json.dumps([order.is_voiced for order in ready_orders])
    }
    return JsonResponse(data)


@login_required()
def current_queue(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       is_canceled=False, is_ready=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        is_canceled=False, content_completed=True, supplement_completed=True,
                                        is_ready=True).order_by('open_time')
    # print open_orders
    # print ready_orders

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
    # print context
    return HttpResponse(template.render(context, request))


@login_required()
def current_queue_ajax(request):
    open_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                       is_canceled=False, is_ready=False).order_by('open_time')
    ready_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        is_canceled=False, content_completed=True, supplement_completed=True,
                                        is_ready=True).order_by('open_time')

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


@login_required()
def cook_interface(request):
    def new_processor(request):
        user = request.user
        staff = Staff.objects.get(user=user)
        if not staff.available:
            staff.available = True
            staff.save()
        context = None
        taken_order_content = None
        taken_orders = Order.objects.filter(prepared_by=staff, open_time__isnull=False,
                                            open_time__contains=datetime.date.today(), is_canceled=False,
                                            content_completed=False,
                                            close_time__isnull=True).order_by('open_time'),
        has_order = False
        if taken_orders[0]:
            taken_order_content = OrderContent.objects.filter(order=taken_orders[0][0],
                                                              menu_item__can_be_prepared_by__title__iexact='Cook',
                                                              finish_timestamp__isnull=True).order_by('id')
            if len(taken_order_content) > 0:
                has_order = True
        # print "Orders: {}".format(taken_orders)
        # print "Order: {}".format(taken_orders[0][0])
        # print "Has order: {}. Content compleated: {}".format(has_order, taken_orders[0][0].content_completed)

        if not has_order:
            free_orders = Order.objects.filter(prepared_by__isnull=True, is_canceled=False,
                                               open_time__contains=datetime.date.today()).order_by('open_time')

            for free_order in free_orders:
                taken_order_content = OrderContent.objects.filter(order=free_order,
                                                                  menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
                    'id')
                taken_order_in_grill_content = OrderContent.objects.filter(order=free_order,
                                                                           grill_timestamp__isnull=False,
                                                                           menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
                    'id')
                # ALERT! Only SuperGuy can handle this amount of shawarma!!!
                if len(taken_order_content) > 6:
                    if staff.super_guy:
                        free_order.prepared_by = staff
                    else:
                        continue
                else:
                    free_order.prepared_by = staff

                if free_order.prepared_by == staff:
                    free_order.save()
                    # print "Free orders prepared_by: {}".format(free_order.prepared_by)
                    context = {
                        'free_order': free_order,
                        'order_content': [{'number': number,
                                           'item': item} for number, item in enumerate(taken_order_content, start=1)],
                        'in_grill_content': [{'number': number,
                                              'item': item} for number, item in
                                             enumerate(taken_order_in_grill_content, start=1)],
                        'staff_category': staff
                    }

                break
        else:
            taken_order_content = OrderContent.objects.filter(order=taken_orders[0][0],
                                                              menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
                'id')
            taken_order_in_grill_content = OrderContent.objects.filter(order=taken_orders[0][0],
                                                                       grill_timestamp__isnull=False,
                                                                       menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
                'id')
            context = {
                'free_order': taken_orders[0][0],
                'order_content': [{'number': number,
                                   'item': item} for number, item in enumerate(taken_order_content, start=1)],
                'in_grill_content': [{'number': number,
                                      'item': item} for number, item in
                                     enumerate(taken_order_in_grill_content, start=1)],
                'staff_category': staff
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
                          'time_in_grill': datetime.datetime.now().replace(
                              tzinfo=None) - product.grill_timestamp.replace(
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

    def new_processor_with_queue(request):
        user = request.user
        staff = Staff.objects.get(user=user)
        if not staff.available:
            staff.available = True
            staff.save()
        context = None
        taken_order_content = None
        new_order = Order.objects.filter(prepared_by=staff, open_time__isnull=False,
                                         open_time__contains=datetime.date.today(), is_canceled=False,
                                         content_completed=False, is_grilling=False,
                                         close_time__isnull=True).order_by('open_time')
        other_orders = Order.objects.filter(prepared_by=staff, open_time__isnull=False,
                                            open_time__contains=datetime.date.today(), is_canceled=False,
                                            close_time__isnull=True).order_by('open_time')
        has_order = False
        if len(new_order)>0:
            new_order = new_order[0]
            taken_order_content = OrderContent.objects.filter(order=new_order,
                                                              menu_item__can_be_prepared_by__title__iexact='Cook',
                                                              finish_timestamp__isnull=True).order_by('id')
            if len(taken_order_content) > 0:
                has_order = True

        # if not has_order:
        #     free_orders = Order.objects.filter(prepared_by__isnull=True, is_canceled=False,
        #                                        open_time__contains=datetime.date.today()).order_by('open_time')
        #
        #     for free_order in free_orders:
        #         taken_order_content = OrderContent.objects.filter(order=free_order,
        #                                                           menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
        #             'id')
        #         taken_order_in_grill_content = OrderContent.objects.filter(order=free_order,
        #                                                                    grill_timestamp__isnull=False,
        #                                                                    menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
        #             'id')
        #         # ALERT! Only SuperGuy can handle this amount of shawarma!!!
        #         if len(taken_order_content) > 6:
        #             if staff.super_guy:
        #                 free_order.prepared_by = staff
        #             else:
        #                 continue
        #         else:
        #             free_order.prepared_by = staff
        #
        #         if free_order.prepared_by == staff:
        #             free_order.save()
        #             # print "Free orders prepared_by: {}".format(free_order.prepared_by)
        #             context = {
        #                 'free_order': free_order,
        #                 'order_content': [{'number': number,
        #                                    'item': item} for number, item in enumerate(taken_order_content, start=1)],
        #                 'in_grill_content': [{'number': number,
        #                                       'item': item} for number, item in
        #                                      enumerate(taken_order_in_grill_content, start=1)],
        #                 'staff_category': staff
        #             }
        #
        #         break
        # else:
        taken_order_content = OrderContent.objects.filter(order=new_order,
                                                          menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
            'id')
        taken_order_in_grill_content = OrderContent.objects.filter(order=new_order,
                                                                   grill_timestamp__isnull=False,
                                                                   menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
            'id')
        context = {
            'free_order': new_order,
            'order_content': [{'number': number,
                               'item': item} for number, item in enumerate(taken_order_content, start=1)],
            'in_grill_content': [{'number': number,
                                  'item': item} for number, item in
                                 enumerate(taken_order_in_grill_content, start=1)],
            'cooks_orders': [{'order': cooks_order,
                              'cook_content_count': len(OrderContent.objects.filter(order=cooks_order,
                                                                                    menu_item__can_be_prepared_by__title__iexact='cook'))}
                             for cooks_order in other_orders],
            'staff_category': staff
        }

        template = loader.get_template('queue/cook_interface_with_queue.html')
        return HttpResponse(template.render(context, request))

    return new_processor_with_queue(request)


@login_required()
def c_i_a(request):
    def new_processor(request):
        user = request.user
        staff = Staff.objects.get(user=user)
        if not staff.available:
            staff.available = True
            staff.save()
        # print u"AJAX from {}".format(user)
        context = None
        taken_order_content = None
        taken_orders = Order.objects.filter(prepared_by=staff, open_time__isnull=False,
                                            open_time__contains=datetime.date.today(), is_canceled=False,
                                            content_completed=False,
                                            close_time__isnull=True).order_by('open_time'),
        has_order = False
        if taken_orders[0]:
            taken_order_content = OrderContent.objects.filter(order=taken_orders[0][0],
                                                              menu_item__can_be_prepared_by__title__iexact='Cook',
                                                              finish_timestamp__isnull=True).order_by('id')
            if len(taken_order_content) > 0:
                has_order = True
        # print "Orders: {}".format(taken_orders)
        # print "Order: {}".format(taken_orders[0][0])
        # print "Has order: {}. Content compleated: {}".format(has_order, taken_orders[0][0].content_completed)

        if not has_order:
            free_orders = Order.objects.filter(prepared_by__isnull=True, is_canceled=False,
                                               open_time__contains=datetime.date.today()).order_by('open_time')

            for free_order in free_orders:
                taken_order_content = OrderContent.objects.filter(order=free_order,
                                                                  menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
                    'id')
                # ALERT! Only SuperGuy can handle this amount of shawarma!!!
                if len(taken_order_content) > 6:
                    if staff.super_guy:
                        free_order.prepared_by = staff
                    else:
                        continue
                else:
                    free_order.prepared_by = staff

                if free_order.prepared_by == staff:
                    free_order.save()
                    # print "Free orders prepared_by: {}".format(free_order.prepared_by)
                    context = {
                        'free_order': free_order,
                        'order_content': [{'number': number,
                                           'item': item} for number, item in enumerate(taken_order_content, start=1)],
                        'staff_category': staff
                    }

                break
        else:
            taken_order_content = OrderContent.objects.filter(order=taken_orders[0][0],
                                                              menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
                'id')
            context = {
                'free_order': taken_orders[0][0],
                'order_content': [{'number': number,
                                   'item': item} for number, item in enumerate(taken_order_content, start=1)],
                'staff_category': staff
            }

        template = loader.get_template('queue/cook_interface_alt_ajax.html')
        data = {
            'html': json.dumps(template.render(context, request))
        }
        return JsonResponse(data)

    def queue_processor(request):
        user = request.user
        staff = Staff.objects.get(user=user)
        if not staff.available:
            staff.available = True
            staff.save()
        context = None
        taken_order_content = None
        new_order = Order.objects.filter(prepared_by=staff, open_time__isnull=False,
                                         open_time__contains=datetime.date.today(), is_canceled=False,
                                         content_completed=False, is_grilling=False,
                                         close_time__isnull=True).order_by('open_time')
        has_order = False
        if len(new_order) > 0:
            new_order = new_order[0]
            taken_order_content = OrderContent.objects.filter(order=new_order,
                                                              menu_item__can_be_prepared_by__title__iexact='Cook',
                                                              finish_timestamp__isnull=True).order_by('id')
            if len(taken_order_content) > 0:
                has_order = True

        taken_order_content = OrderContent.objects.filter(order=new_order,
                                                          menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
            'id')
        taken_order_in_grill_content = OrderContent.objects.filter(order=new_order,
                                                                   grill_timestamp__isnull=False,
                                                                   menu_item__can_be_prepared_by__title__iexact='Cook').order_by(
            'id')
        context = {
            'selected_order': new_order,
            'order_content': [{'number': number,
                               'item': item} for number, item in enumerate(taken_order_content, start=1)],
            'staff_category': staff
        }
        template = loader.get_template('queue/selected_order_content.html')
        data = {
            'success': True,
            'html': template.render(context, request)
        }

        return JsonResponse(data=data)

    return queue_processor(request)


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
        'maker': order_info.prepared_by,
        'staff_category': StaffCategory.objects.get(staff__user=request.user),
        'order_content': current_order_content,
        'ready': order_info.content_completed and order_info.supplement_completed,
        'serveries': Servery.objects.all()
    }
    return HttpResponse(template.render(context, request))


def print_order(request, order_id):
    order_info = get_object_or_404(Order, id=order_id)
    order_info.printed = True
    order_info.save()
    order_content = OrderContent.objects.filter(order_id=order_id).values('menu_item__title', 'menu_item__price',
                                                                          'note').annotate(
        count_titles=Count('menu_item__title')).annotate(count_notes=Count('note'))
    template = loader.get_template('queue/print_order_wh.html')
    context = {
        'order_info': order_info,
        'order_content': order_content
    }

    cmd = 'echo "{}"'.format(template.render(context, request)) + " | lp -h " + PRINTER_URL
    scmd = cmd.encode('utf-8')
    os.system(scmd)

    return HttpResponse(template.render(context, request))


def voice_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_voiced = False
    order.save()

    return HttpResponse()


def unvoice_order(request):
    daily_number = request.POST.get('daily_number', None)
    data = {
        'success': False
    }
    if daily_number:
        order = get_object_or_404(Order, daily_number=daily_number, open_time__contains=datetime.date.today())
        order.is_voiced = True
        order.save()
        data = {
            'success': True
        }

    return JsonResponse(data=data)


def select_order(request):
    order_id = request.POST.get('order_id', None)
    data = {
        'success': False
    }
    if order_id:
        context = {
            'selected_order': get_object_or_404(Order, id=order_id),
            'order_content': [{'number': number,
                               'item': item} for number, item in enumerate(OrderContent.objects.filter(order__id=order_id,
                                                         menu_item__can_be_prepared_by__title__iexact='Cook'), start=1)]
        }
        template = loader.get_template('queue/selected_order_content.html')
        data = {
            'success': True,
            'html': template.render(context, request)
        }

    return JsonResponse(data=data)


def voice_all(request):
    today_orders = Order.objects.filter(open_time__contains=datetime.date.today(), close_time__isnull=True,
                                        is_ready=True)
    for order in today_orders:
        order.is_voiced = False
        order.save()

    return HttpResponse()


@login_required()
@permission_required('queue.add_order')
def make_order(request):
    servery_ip = request.META.get('HTTP_X_REAL_IP', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
    # servery_ip = '127.0.0.1'
    content = json.loads(request.POST['order_content'])
    is_paid = json.loads(request.POST['is_paid'])
    paid_with_cash = json.loads(request.POST['paid_with_cash'])
    cook_choose = request.POST['cook_choose']
    servery = Servery.objects.get(ip_address=servery_ip)
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
    super_guy = Staff.objects.filter(super_guy=True, user__last_login__contains=datetime.date.today(),
                                     staff_category__title__iexact='Cook')
    # cooks = Staff.objects.filter(user__last_login__contains=datetime.date.today(), staff_category__title__iexact='Cook')
    cooks = Staff.objects.filter(available=True, staff_category__title__iexact='Cook')

    data = {
        "daily_number": order.daily_number
    }
    if cook_choose == 'auto':
        min_index = 0
        min_count = 100
        for cook_index in range(0, len(cooks)):
            cooks_order_content = OrderContent.objects.filter(order__prepared_by=cooks[cook_index],
                                                              order__open_time__contains=datetime.date.today(),
                                                              order__is_canceled=False, order__close_time__isnull=True)
            if min_count > len(cooks_order_content):
                min_count = len(cooks_order_content)
                min_index = cook_index

        if len(super_guy) > 0:
            if len(content) > 6:
                order.prepared_by = super_guy[0]
            else:
                order.prepared_by = cooks[min_index]
        else:
            order.prepared_by = cooks[min_index]
    else:
        order.prepared_by = Staff.objects.get(id=int(cook_choose))
    content_to_send = []
    order.servery = servery
    order.save()

    total = 0
    content_presence = False
    supplement_presence = False
    for item in content:
        for i in range(0, int(item['quantity'])):
            new_order_content = OrderContent(order=order, menu_item_id=item['id'], note=item['note'])
            new_order_content.save()
            menu_item = Menu.objects.get(id=item['id'])
            if menu_item.can_be_prepared_by.title == 'Cook':
                content_presence = True
            if menu_item.can_be_prepared_by.title == 'Operator':
                supplement_presence = True
            total += menu_item.price

        content_to_send.append(
            {
                'item_id': item['id'],
                'quantity': item['quantity']
            }
        )

    order.total = total
    order.content_completed = not content_presence
    order.supplement_completed = not supplement_presence
    order.save()
    if order.is_paid:
        print "Sending request to " + order.servery.ip_address
        print order
        requests.post('http://' + order.servery.ip_address + ':' + LISTNER_PORT, json=prepare_json_check(order))
        print "Request sent."

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
    # print 'Trying to take 1.'
    product_id = request.POST.get('id', None)
    # print request.POST
    data = {
        'success': json.dumps(False)
    }
    if product_id:
        product = OrderContent.objects.get(id=product_id)
        if product.staff_maker is None:
            staff_maker = Staff.objects.get(user=request.user)
            product.staff_maker = staff_maker
            product.start_timestamp = datetime.datetime.now()
            product.save()
            data = {
                'success': json.dumps(True)
            }
        else:
            data = {
                'success': json.dumps(False),
                'staff_maker': 'TEST_MAKER'
            }
    # print 'Trying to take 2.'

    return JsonResponse(data)


# @login_required()
# @permission_required('queue.can_cook')
def to_grill(request):
    product_id = request.POST.get('id', None)
    if product_id:
        product = OrderContent.objects.get(pk=product_id)
        product.grill_timestamp = datetime.datetime.now()
        product.is_in_grill = True
        if product.staff_maker is None:
            staff_maker = Staff.objects.get(user=request.user)
            product.staff_maker = staff_maker
            product.start_timestamp = datetime.datetime.now()
        product.save()
        order_content = OrderContent.objects.filter(order_id=product.order_id)
        flag = True
        for item in order_content:
            if not item.is_in_grill:
                flag = False
        if flag:
            product.order.is_grilling = True
            product.order.save()
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
            print "saving"
            product.order.save()
            print product.order.content_completed
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


# @login_required()
# @permission_required('queue.can_cook')
def finish_all_content(request):
    order_id = request.POST.get('id', None)
    if order_id:
        order = Order.objects.get(id=order_id)
        products = OrderContent.objects.filter(order=order, menu_item__can_be_prepared_by__title__iexact='Cook')
        for product in products:
            product.is_in_grill = False
            product.finish_timestamp = datetime.datetime.now()
            if product.start_timestamp is None:
                product.start_timestamp = datetime.datetime.now()
            if product.staff_maker is None:
                product.staff_maker = Staff.objects.get(user=request.user)
            product.save()
        order.content_completed = True
        # print "saving"
        order.save()
        data = {
            'success': True
        }
    else:
        data = {
            'success': False
        }

    return JsonResponse(data)


# @login_required()
# @permission_required('queue.can_cook')
def grill_all_content(request):
    order_id = request.POST.get('order_id', None)
    if order_id:
        order = Order.objects.get(id=order_id)
        products = OrderContent.objects.filter(order=order, menu_item__can_be_prepared_by__title__iexact='Cook')
        for product in products:
            product.start_timestamp = datetime.datetime.now()
            product.grill_timestamp = datetime.datetime.now()
            product.is_in_grill = True
            product.staff_maker = Staff.objects.get(user=request.user)
            product.save()
        order.is_grilling = True
        # print "saving"
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
            product.order.supplement_completed = True
            product.order.save()

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
    servery_choose = request.POST.get('servery_choose', None)
    if order_id:
        order = Order.objects.get(id=order_id)
        order.supplement_completed = True
        order.is_ready = True
        check_auto = servery_choose == 'auto' or servery_choose is None
        if not check_auto:
            servery = Servery.objects.get(id=servery_choose)
            order.servery = servery

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
def pay_order(request):
    order_id = request.POST.get('id', None)
    if order_id:
        order = Order.objects.get(id=order_id)
        order.is_paid = True
        order.save()
        print "Sending request to " + order.servery.ip_address
        # print order
        requests.post('http://' + order.servery.ip_address + ':' + LISTNER_PORT, json=prepare_json_check(order))
        print "Request sent."
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
    pay_rows = []
    number = 1
    sum = 0
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

    cook_name = u"{}".format(order.prepared_by.user.first_name)
    order_number = str(order.daily_number)

    print u"Cash: {}".format(aux_query[0]['order__paid_with_cash'])
    if aux_query[0]['order__paid_with_cash']:
        pay_rows.append({
            u"НомерСтроки": 1,
            u"ВидОплаты": {
                "TYPE": "СправочникСсылка.ВидыОплатЧекаККМ",
                "UID": "5715e4bd-767b-11e6-82c6-28c2dd30392b"
            },
            u"Сумма": sum,
            u"ДанныеПереданыВБанк": False
        })
    else:
        pay_rows.append({
            u"НомерСтроки": 1,
            u"ВидОплаты": {
                "TYPE": "СправочникСсылка.ВидыОплатЧекаККМ",
                "UID": "8414dfc8-7683-11e6-8251-002215bf2d6a"
            },
            u"ЭквайринговыйТерминал": {
                "TYPE": "СправочникСсылка.ЭквайринговыеТерминалы",
                "UID": "8414dfc9-7683-11e6-8251-002215bf2d6a"
            },
            u"Сумма": sum,
            u"ДанныеПереданыВБанк": False
        })

    aux_dict = {
        "OBJECT": True,
        "NEW": "Документы.ЧекККМ.СоздатьДокумент()",
        "SAVE": True,
        "Проведен": False,
        "Ссылка": {
            "TYPE": "ДокументСсылка.ЧекККМ",
            "UID": "0000-0000-0000-0000"
        },
        "ПометкаУдаления": False,
        "Дата": {
            "TYPE": "Дата",
            "UID": "ДДДДДД"
        },
        "Номер": "ЯЯЯЯЯЯ",
        "АналитикаХозяйственнойОперации": {
            "TYPE": "СправочникСсылка.АналитикаХозяйственныхОпераций",
            "UID": "5715e4c9-767b-11e6-82c6-28c2dd30392b"
        },
        "БонусыНачислены": False,
        "ВидОперации": {
            "TYPE": "ПеречислениеСсылка.ВидыОперацийЧекККМ",
            "UID": "Продажа"
        },
        "КассаККМ": {
            "TYPE": "СправочникСсылка.КассыККМ",
            "UID": "8414dfc5-7683-11e6-8251-002215bf2d6a"
        },
        "Магазин": {
            "TYPE": "СправочникСсылка.Магазины",
            "UID": "cc442ddb-767b-11e6-82c6-28c2dd30392b"
        },
        "НомерЧекаККМ": None,
        "Организация": {
            "TYPE": "СправочникСсылка.Организации",
            "UID": "1d68a28e-767b-11e6-82c6-28c2dd30392b"
        },
        "Ответственный": {
            "TYPE": "СправочникСсылка.Пользователи",
            "UID": "1d68a28d-767b-11e6-82c6-28c2dd30392b"
        },
        "ОтработанПереход": False,
        "СкидкиРассчитаны": True,
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
            "ROWS": pay_rows
        },
        "Повар": cook_name,
        "НомерОчереди": order_number
    }
    print "JSON formed!"
    return json.dumps(aux_dict, ensure_ascii=False)
