from .models import *
from django.contrib.auth.models import User

from django import forms
from .models import *
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ("user","image",'status')



PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)
#
# class CheckoutForm(forms.ModelForm):
#     class Meta:
#         model = Address
#         fields = ('name','contact','street_address','alternative_no','pincode','city','state','landmarks','locality')



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        "class":"form-control",
        "placeholder":'Promo Code',
        'aria-label':'Recipient\'s username',
        'aria-describedby':'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows':4
    }))
    email = forms.EmailField()
