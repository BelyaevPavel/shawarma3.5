from django import forms
from django.contrib.admin import widgets

from .models import Order, OrderContent, Staff


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('id', 'daily_number', 'open_time', 'close_time',
                  'prepared_by')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['prepared_by'] = forms.CharField()
        self.fields['date'].widget = widgets.AdminDateWidget()
        self.fields['start_time'].widget = widgets.AdminTimeWidget()
        self.fields['end_time'].widget = widgets.AdminTimeWidget()