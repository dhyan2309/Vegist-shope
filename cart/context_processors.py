from .cart import Cart


def cart_context(request):
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_item_count': len(cart),
        'cart_subtotal': cart.get_subtotal_price(),
        'cart_total': cart.get_total_price(),
        'free_shipping_remaining': cart.get_free_shipping_remaining(),
        'free_shipping_progress': cart.get_free_shipping_progress(),
        'cart_coupon': cart.coupon,
        'cart_discount': cart.get_discount_amount(),
        'cart_shipping': cart.get_shipping_price(),
    }
