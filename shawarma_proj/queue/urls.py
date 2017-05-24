from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^order/(?P<order_id>[0-9]+)/', views.order_content, name="order content"),
]