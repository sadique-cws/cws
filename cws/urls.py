from django.contrib import admin
from django.urls import path,include
from students.views import *
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PublicHomeView.as_view(),name="homepage"),
    path('course/<slug>/', CourseDetailView.as_view(), name="course"),
    path('ordersummary/', OrderSummaryView.as_view(), name="order-summary"),
    path('add-to-cart/<slug>/', AddToCartView.as_view(), name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart,name="remove-from-cart"),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('payment/', PaymentView.as_view(), name="payment"),
    path('student/', include('students.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/complete_profile/', CompleteProfileView.as_view(),name="complete_profile"),
    path('login_success/', login_success, name='login_success'),
] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)