from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:category_slug>/', views.shop, name='shop_category_alias'),
    path('category/<slug:category_slug>/', views.shop, name='shop_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('quick-view/<int:product_id>/', views.quick_view_json, name='quick_view_json'),
    path('deals/', views.deals_view, name='deals'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('recipes/', views.recipes_view, name='recipes'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
