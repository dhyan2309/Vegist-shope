from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'first_name', 'last_name', 'email', 'phone', 'total', 'payment_method', 'status', 'is_paid', 'razorpay_payment_id', 'created_at')
    list_filter = ('status', 'is_paid', 'payment_method', 'created_at')
    list_editable = ('status', 'is_paid')
    search_fields = ('order_number', 'first_name', 'last_name', 'email', 'phone', 'razorpay_payment_id', 'razorpay_order_id')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at', 'updated_at')
