from django.contrib import admin
from .models import Category, Product, Review, NewsletterSubscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'unit', 'stock', 'is_organic', 'is_featured', 'is_trending', 'is_deal_of_the_day')
    list_filter = ('category', 'is_organic', 'is_featured', 'is_trending', 'is_deal_of_the_day')
    list_editable = ('price', 'old_price', 'stock', 'is_featured', 'is_trending', 'is_deal_of_the_day')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user_name', 'comment', 'product__name')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
