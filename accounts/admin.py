from django.contrib import admin
from .models import Profile, WishlistItem


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country')
    search_fields = ('user__username', 'user__email', 'phone', 'city')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'user__username')
