from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.menu, name='menu'),
    url(r'^order/(?P<order_id>[0-9]+)/$', views.order_content, name="order_content"),
    url(r'^ajax/make_order', views.make_order, name="make_order"),
    url(r'^ajax/close_order', views.close_order, name="close_order"),
    url(r'ajax/take', views.take, name="take"),
    url(r'ajax/to_grill', views.to_grill, name="to_grill"),
    url(r'ajax/finish_cooking', views.finish_cooking, name="finish_cooking"),
    url(r'^ajax/current_queue', views.current_queue_ajax, name="current_queue_ajax"),
    url(r'^current_queue', views.current_queue, name="current_queue"),
    url(r'^production_queue', views.production_queue, name="production_queue"),
    url(r'^cook_interface', views.cook_interface, name="cook_interface"),
]
