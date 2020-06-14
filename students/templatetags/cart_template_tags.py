from django import template
from students.models import *


register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user,ordered=False)
        if qs.exists():
            return qs[0].items.count()

    return 0

@register.filter
def Item_Is_Exit(user,slug):
    if user.is_authenticated:
        qs = OrderItem.objects.filter(user=user,ordered=False,item__slug=slug)
        if qs.exists():
            return True
    return False

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def multiply(value, arg):
    return int(arg) * int(value)