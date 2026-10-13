from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('decrement/<int:product_id>/', views.cart_decrement, name='cart_decrement'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('drawer-data/', views.cart_drawer_data, name='cart_drawer_data'),
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
]
