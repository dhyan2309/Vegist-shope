from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from store.models import Product
from .models import Coupon
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Stock validation
    if product.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({
                'success': False,
                'message': f'Sorry, "{product.name}" is currently out of stock.'
            }, status=400)
        messages.error(request, f'Sorry, "{product.name}" is currently out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'store:home'))
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    if quantity > product.stock:
        quantity = product.stock
        
    override = request.POST.get('override', 'false').lower() == 'true'
    cart.add(product=product, quantity=quantity, override_quantity=override)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" added to cart!',
            'item_count': len(cart),
            'subtotal': str(cart.get_subtotal_price()),
            'total': str(cart.get_total_price()),
            'free_shipping_progress': cart.get_free_shipping_progress(),
            'free_shipping_remaining': str(cart.get_free_shipping_remaining()),
            'cart_items': [
                {
                    'id': item['product'].id,
                    'name': item['product'].name,
                    'price': str(item['price']),
                    'total_price': str(item['total_price']),
                    'quantity': item['quantity'],
                    'unit': item['product'].unit,
                    'image_url': item['product'].image.url if item['product'].image else '/static/images/cat_vegetables.jpg',
                    'url': item['product'].get_absolute_url()
                }
                for item in cart
            ]
        })

    messages.success(request, f'"{product.name}" was added to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))


@require_POST
def cart_decrement(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.decrement(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'item_count': len(cart),
            'subtotal': str(cart.get_subtotal_price()),
            'total': str(cart.get_total_price()),
            'free_shipping_progress': cart.get_free_shipping_progress(),
            'free_shipping_remaining': str(cart.get_free_shipping_remaining()),
        })

    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" removed from cart',
            'item_count': len(cart),
            'subtotal': str(cart.get_subtotal_price()),
            'total': str(cart.get_total_price()),
            'free_shipping_progress': cart.get_free_shipping_progress(),
            'free_shipping_remaining': str(cart.get_free_shipping_remaining()),
        })

    messages.info(request, f'"{product.name}" removed from cart.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


def cart_drawer_data(request):
    cart = Cart(request)
    items = []
    for item in cart:
        items.append({
            'id': item['product'].id,
            'name': item['product'].name,
            'price': str(item['price']),
            'total_price': str(item['total_price']),
            'quantity': item['quantity'],
            'unit': item['product'].unit,
            'image_url': item['product'].image.url if item['product'].image else '/static/images/cat_vegetables.jpg',
            'url': item['product'].get_absolute_url()
        })

    return JsonResponse({
        'item_count': len(cart),
        'subtotal': str(cart.get_subtotal_price()),
        'total': str(cart.get_total_price()),
        'free_shipping_progress': cart.get_free_shipping_progress(),
        'free_shipping_remaining': str(cart.get_free_shipping_remaining()),
        'items': items
    })


@require_POST
def apply_coupon(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    try:
        coupon = Coupon.objects.get(code__iexact=code)
        if coupon.is_valid():
            request.session['coupon_id'] = coupon.id
            messages.success(request, f'Promo code "{coupon.code}" applied! You saved {coupon.discount_percent}%.')
        else:
            messages.error(request, 'This promo coupon has expired or is inactive.')
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code. Try VEGIST20 for 20% discount!')

    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.info(request, 'Coupon removed.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))
