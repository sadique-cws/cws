from django.contrib import admin
from django.urls import path,re_path
from .views import *
from students import views
urlpatterns = [
    path('', HomeView.as_view(),name="student_homepage"),
    path('profile/', ProfileView.as_view(),name="profile"),
    path('update-profile/', UpdateProfileView.as_view(),name="update-profile"),
    path('my-course/', StudentCourseView.as_view(),name="my-course"),
    path('dashboard/', HomeView.as_view(),name="dashboard"),
    path('my-payments/', StudentPaymentView.as_view(),name="my-payments"),
    path('my-payments/<int:pk>/', payment_receipt,name="payment_receipt"),
    path('repay/', RePaymentView.as_view(),name="repayments"),
    path('response/', views.FirstPaymentView.as_view(),name="first-paymentview"),
]
