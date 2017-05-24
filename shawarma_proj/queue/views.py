# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Menu, Order, Staff, OrderContent
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse


# Create your views here.
def index(request):
    menu_items = Menu.objects.order_by('price')
    template = loader.get_template('queue/index.html')
    context = {
        'menu_items': menu_items,
    }
    return HttpResponse(template.render(context, request))

def order_content(request, order_id):
    orderContent = get_object_or_404(OrderContent, order=order_id)
    return render()