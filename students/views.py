from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,View,TemplateView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import Checksum
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from students.utils import VerifyPaytmResponse
from django.utils import timezone
from .forms import *
import random
import string
from django.templatetags.static import static
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def login_success(request):
    if request.user.groups.exclude(name="students").exists():
        return redirect("admin")
    else:
        if request.user.student.contact == None:
            return redirect("complete_profile")
        else:
            return redirect("dashboard")



class CompleteProfileView(LoginRequiredMixin,View):
    def get(self,request):

        userform =  StudentForm(request.POST or None,instance=request.user.student)
        return render(self.request,'profile_details.html',{"form1":userform})

    def post(self,request):
        userform =  StudentForm(request.POST or None,instance=request.user.student)
        if userform.is_valid():
            userform.save()
            messages.success(self.request,"Account Updated Successfully")
            return redirect("dashboard")
        else:
            messages.error(self.request,"something went wrong try again")
            return redirect('complete_profile')


    template_name = "profile_details.html"


class PublicHomeView(ListView):
    model = Course
    template_name = "home.html"


class CourseDetailView(DetailView):
    def get(self,request,*args,**kwargs):
        data = {
            'object':Course.objects.get(slug=self.kwargs['slug']),
            'object_list':Course.objects.all().order_by('?').exclude(slug=self.kwargs['slug'])[:4]
        }
        return render(self.request,'item.html',data)



class HomeView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        if self.request.user.student.contact == None:
            return redirect("complete_profile")
        order = Order.objects.filter(user=self.request.user, ordered=True)
        data = {"order":order}
        return render(self.request,"students/dashboard.html",data)


class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = "students/profile.html"


class StudentCourseView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        if self.request.user.student.contact == None:
            return redirect("complete_profile")
        order = Order.objects.filter(user=self.request.user,ordered=True)
        context = {"order":order}
        return render(self.request, 'students/my_course.html',context)

class StudentPaymentView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        if self.request.user.student.contact == None:
            return redirect("complete_profile")
        context = {
            "order":Order.objects.filter(user=self.request.user,ordered=True)
        }
        return render(self.request,"students/my_payments.html",context)


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            context = {"object":order,"DISPLAY_COUPON_FORM":True,"couponform":CouponForm}
        except ObjectDoesNotExist:
            messages.warning(self.request,"you do not have an active order")
            return redirect("/")

        return render(self.request, 'order_summary.html',context)

    model = Order
    template_name = 'order_summary.html'

class PaymentView(View):
       def post(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        student = Student.objects.get(user_id=self.request.user.id)

        # create the payment
        pay_type = self.request.POST.get("type",None)

        if pay_type == "1":
            amount = order.get_total()
        elif pay_type == "2":
            amount = order.get_1st_installment()
        else:
            return redirect("order-summary")



        order_id = Checksum.__id_generator__()
        bill_amount = str(amount)
        data_dict = {
            'MID': settings.PAYTM_MERCHANT_ID,
            'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
            'WEBSITE': settings.PAYTM_WEBSITE,
            'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
            'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
            'MOBILE_NO': str(student.contact),
            'EMAIL': str(student.email),
            'CUST_ID': str(self.request.user.id),
            'ORDER_ID': order_id,
            'TXN_AMOUNT': bill_amount,
            'MERC_UNQ_REF': str(self.request.user.id),  # used to save data in response

        }  # This data should ideally come from database
        data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, settings.PAYTM_MERCHANT_KEY)
        context = {
            'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
            'comany_name': settings.PAYTM_COMPANY_NAME,
            'data_dict': data_dict
        }
        return render(self.request, 'payments/payment.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class FirstPaymentView(View):
       def post(self,request,*args,**kwargs):

        # create the payment
        resp = VerifyPaytmResponse(self.request)

        # payments successful

        #work for payment system
        if resp['verified']:
            if len(resp['paytm']['MERC_UNQ_REF']) < 10:
                get_user = User.objects.get(id=resp['paytm']['MERC_UNQ_REF'])
                order = Order.objects.get(user=get_user, ordered=False)
                pay = Payment()
                pay.txn_id = resp['paytm']["TXNID"]
                pay.user = get_user
                if order.get_total() > float(resp['paytm']["TXNAMOUNT"]):
                    pay.type = 2
                else:
                    pay.type = 1
                pay.due_amount = order.get_total() - float(resp['paytm']["TXNAMOUNT"])
                pay.amount = resp['paytm']["TXNAMOUNT"]
                pay.bank_txnid = resp['paytm']['BANKTXNID']
                pay.payment_type = resp['paytm']['PAYMENTMODE']
                pay.order_id = resp['paytm']['ORDERID']
                pay.txn_date = resp['paytm']['TXNDATE']
                pay.status = True
                pay.save()

                # assign the payment to the order
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True

                order.payment.add(pay)

                # todo : assign ref code

                order.ref_code = create_ref_code()
                order.save()

            else:
                #work for repayment system
                order = Order.objects.get(ref_code=resp['paytm']['MERC_UNQ_REF'], ordered=True)
                get_user = User.objects.get(id=order.user.id)

                pay = Payment()
                pay.txn_id = resp['paytm']["TXNID"]
                pay.user = get_user
                if order.get_total() > float(resp['paytm']["TXNAMOUNT"]):
                    pay.type = 2
                else:
                    pay.type = 1
                due = 0.0
                for i in order.payment.all():
                    due = i.due_amount

                pay.due_amount =  due - float(resp['paytm']["TXNAMOUNT"])
                pay.amount = resp['paytm']["TXNAMOUNT"]
                pay.bank_txnid = resp['paytm']['BANKTXNID']
                pay.payment_type = resp['paytm']['PAYMENTMODE']
                pay.order_id = resp['paytm']['ORDERID']
                pay.txn_date = resp['paytm']['TXNDATE']
                pay.status = True
                pay.save()

                order.payment.add(pay)

            messages.info(self.request, "successfully payment done")
            return redirect('my-payments')
        else:
            messages.error(self.request, "Payment Fail Please Try Again")
            if len(resp['paytm']['MERC_UNQ_REF']) < 10:
                return redirect('order-summary')
            else:
                return redirect('my-payments')

class RePaymentView(View):
       def post(self,request,*args,**kwargs):

        # create the payment
        student = Student.objects.get(user_id=self.request.user.id)
        amount = float(self.request.POST.get("amount",None))
        ref_code = self.request.POST.get("ref_code",None)
        order_id = Checksum.__id_generator__()


        # gatway work

        data_dict = {
            'MID': settings.PAYTM_MERCHANT_ID,
            'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
            'WEBSITE': settings.PAYTM_WEBSITE,
            'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
            'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
            'MOBILE_NO': str(student.contact),
            'EMAIL': str(student.email),
            'CUST_ID': str(self.request.user.id),
            'ORDER_ID': order_id,
            'TXN_AMOUNT': str(amount),
            'MERC_UNQ_REF': str(ref_code),  # used to save data in response

        }  # This data should ideally come from database
        data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, settings.PAYTM_MERCHANT_KEY)
        context = {
            'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
            'comany_name': settings.PAYTM_COMPANY_NAME,
            'data_dict': data_dict
        }
        return render(self.request, 'payments/payment.html', context)


def check_coupon(request,code):

    try:
        coupon = Coupon.objects.get(code=code)
        return True
    except ObjectDoesNotExist:
        return False

def get_coupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request,"this coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(LoginRequiredMixin,View):
    def post(self,*args,**kwargs):
        if self.request.method == "POST":
            form = CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get("code")
                    if check_coupon(self.request,code):
                        order = Order.objects.get(user=self.request.user, ordered=False)
                        order.coupon = get_coupon(self.request,code)
                        order.save()
                        messages.success(self.request, "Successfully added coupon")
                        return redirect("order-summary")
                    else:
                        messages.error(self.request, "Invalid coupon Try Again")
                        return redirect("order-summary")

                except ObjectDoesNotExist:
                    messages.info(self.request,"you do not have an active order")
                    return redirect("order-summary")


@login_required()
def remove_from_cart(request, slug):
    item = get_object_or_404(Course, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(course__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                course=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.error(request, "This item was removed from your cart.")
            return redirect("order-summary")
        else:
            messages.error(request, "This item was not in your cart")
            return redirect("course", slug=slug)
    else:
        messages.warning(request, "You do not have an active order")
        return redirect("course", slug=slug)


class AddToCartView(LoginRequiredMixin,View):
    def get(self,request, slug,*args,**kwargs):
        item = get_object_or_404(Course,slug=slug)

        order_item, created = OrderItem.objects.get_or_create(
            course=item,
            user=request.user,
            ordered=False,
        )
        order_qs = Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(course__slug=item.slug).exists():
                messages.info(request,"this course already exist in a cart")
                return redirect("order-summary")
            else:
                order.items.add(order_item)
                messages.success(request,"this item was added to your cart")
                return redirect("order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user,ordered_date=ordered_date)
            order.items.add(order_item)
            messages.success(request,"this item was added to your cart")
            return redirect("order-summary")

class UpdateProfileView(LoginRequiredMixin,View):
    def get(self,request):
        userform =  StudentForm(request.POST or None,instance=request.user.student)
        return render(self.request,'students/update_profile.html',{"form1":userform})

    def post(self,request):
        userform =  StudentForm(request.POST or None,instance=request.user.student)
        if userform.is_valid():
            userform.save()
            return redirect("dashboard")

    template_name = "students/profile.html"


def payment_receipt(request,pk):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    logo = "http://localhost:8000/static/newlogo.png"

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    p.drawImage(logo,1,1,200,100)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')