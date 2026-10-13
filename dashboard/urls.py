from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home
    path('', views.dashboard_home, name='home'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    
    # Orders
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Categories
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    
    # Coupons
    path('coupons/', views.coupons_list, name='coupons_list'),
    path('coupons/toggle/<int:pk>/', views.coupon_toggle, name='coupon_toggle'),
    
    # Reviews
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/delete/<int:pk>/', views.review_delete, name='review_delete'),
]
