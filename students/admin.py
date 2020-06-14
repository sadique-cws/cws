from django.contrib import admin

# Register your models here.
from .models import *
from django.utils.html import format_html
from liststyle import ListStyleAdminMixin
from django.utils.text import slugify



class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'coupon'
    ]
    list_filter = ['ordered']
    search_fields = [
        'user__username',
        'ref_code'
    ]


class StudentAdmin(admin.ModelAdmin):

    list_display = [
        'upper_name',
        'gender',
        'father_name',
        'contact',
        'address',
        'city',
        'state',
        'status',
    ]
    list_filter = [
        'gender',
        'status'
    ]
    ordering = ['id']


    def upper_name(self,obj):
        return ("%s" % (obj.name)).capitalize()

    upper_name.short_description = "fullname"




class PaymentAdmin(admin.ModelAdmin,ListStyleAdminMixin):


    list_display = [
        'txn_id',
        'user',
        'amount',
        'due_amount_html',
        'type',
        'order_id',
        'txn_date',
        'payment_type',
        'bank_txnid',
        'status',

    ]

    def due_amount_html(self,obj):

        if obj.due_amount == 0.0:
            return format_html(
                '<span style="color:green">{}</span>',
                obj.due_amount
            )
        else:
            return format_html(
                '<span style="color:red">{}</span>',
                obj.due_amount
            )

    def get_row_css(self, obj, index):
        if obj.due_amount == 0.0:
            return 'green'
        return 'red'


admin.site.unregister(User)


class UserAdmin(admin.ModelAdmin):
    list_display = ['username','get_payments']

    def get_payments(self, obj):
        return sum([p.amount for p in Payment.objects.filter(user=obj.id)])

    list_display_links = ['username',]



class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'price',
        'discount_price',
        'assignments',
        'duration',
        'status',
    ]


    prepopulated_fields = {'slug': ('title',)}

admin.site.register(User,UserAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Coupon)


