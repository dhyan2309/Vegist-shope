from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/razorpay/verify/', views.razorpay_verify_view, name='razorpay_verify'),
    path('payment/razorpay/switch-cod/<str:order_number>/', views.switch_cod_view, name='switch_cod'),
    path('payment/razorpay/<str:order_number>/', views.razorpay_payment_view, name='razorpay_payment'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('detail/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
