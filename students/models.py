from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User,Group,Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings



GENDER_CHOICE = (
    ("M","MALE"),
    ("F","FEMALE")
)
CITY_CHOICE = (
    ("PUR","PURNEA"),
)
STATE_CHOICE = (
    ("BR","BIHAR"),
)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=200,blank=True)
    father_name = models.CharField(max_length=200,blank=True)
    contact = models.IntegerField(blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    gender = models.CharField(max_length=2,choices=GENDER_CHOICE,blank=True)
    address = models.CharField(max_length=200,null=True)
    city = models.CharField(max_length=3,choices=CITY_CHOICE,null=True)
    state = models.CharField(max_length=3,choices=STATE_CHOICE,null=True)
    education_qualification = models.CharField(max_length=200,null=True)
    name_of_institute = models.CharField(max_length=200,null=True)
    image = models.ImageField(upload_to="students/dp/",null=True)
    status = models.BooleanField(default=False)
    date_of_admission = models.DateField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    g = instance.groups.filter(name="students")
    if created and not g.exists():
        Student.objects.create(user=instance)
        group = Group.objects.get(name="students")
        instance.groups.add(group)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.student.save()



class Course(models.Model):
    title = models.CharField(max_length=200)
    instructor = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField(max_length=200)
    discount_price = models.FloatField(max_length=200)
    assignments = models.IntegerField(default=1)
    image = models.ImageField(upload_to="course/image",blank=True)
    duration = models.IntegerField()
    slug = models.SlugField()
    status = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("course",kwargs={
            'slug':self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.title
                                            


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.title

    def get_amount_saved(self):
        return self.course.price - self.course.discount_price

    def total_discount_percentage_price(self):
        return int(100-(self.course.discount_price/self.course.price)*100)

    
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    being_delivered = models.BooleanField(default=False)
    payment = models.ManyToManyField('Payment')
    coupon = models.ForeignKey('Coupon',on_delete=models.SET_NULL,blank=True,null=True)


    def get_total(self):
        total = 0
        for order_item in self.items.all():
            if order_item.course.discount_price:
                total += order_item.course.discount_price
            else:
                total += order_item.course.price

        if self.coupon:
            total -= self.coupon.amount

        return total

    def get_item_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.course.price

        return total

    def get_1st_installment(self):
        total = self.get_total()
        return total*0.4


    def get_total_amount_saved(self):
        return self.get_item_total() - self.get_total()


PAY_TYPE_CHOICE = (
    ("1","FULL"),
    ("2","Installment")
)


class Payment(models.Model):
    txn_id = models.CharField(max_length=400)
    order_id = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,blank=True,null=True)
    amount = models.FloatField()
    due_amount = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1,choices=PAY_TYPE_CHOICE)
    status = models.BooleanField(default="False")
    payment_type = models.CharField(max_length=15,null=True,blank=True)
    bank_txnid =  models.CharField(max_length=100,null=True,blank=True)
    txn_date = models.DateTimeField(null=True,blank=True)


    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    amount = models.FloatField()

    def __str__(self):
        return self.code

