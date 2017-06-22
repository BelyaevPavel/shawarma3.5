from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^order/(?P<order_id>[0-9]+)/$', views.order_content, name="order_content"),
    url(r'^ajax/make_order', views.make_order, name="make_order"),
    url(r'ajax/take', views.take, name="take"),
    url(r'^current_queue', views.current_queue, name="current_queue"),
    url(r'^production_queue', views.production_queue, name="production_queue"),
]
