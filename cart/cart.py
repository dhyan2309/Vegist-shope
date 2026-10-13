from decimal import Decimal
from django.conf import settings
from store.models import Product
from .models import Coupon


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = max(1, quantity)
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def decrement(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] -= 1
            if self.cart[product_id]['quantity'] <= 0:
                self.remove(product)
            else:
                self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        for product_id, item_data in self.cart.items():
            product = product_map.get(str(product_id))
            if product:
                price = Decimal(str(item_data['price']))
                qty = int(item_data['quantity'])
                yield {
                    'product': product,
                    'price': price,
                    'quantity': qty,
                    'total_price': price * qty,
                }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                coupon = Coupon.objects.get(id=self.coupon_id)
                if coupon.is_valid():
                    return coupon
            except Coupon.DoesNotExist:
                return None
        return None

    def get_discount_amount(self):
        if self.coupon:
            return round((self.coupon.discount_percent / Decimal(100)) * self.get_subtotal_price(), 2)
        return Decimal('0.00')

    def get_shipping_price(self):
        subtotal = self.get_subtotal_price()
        if subtotal == Decimal('0.00'):
            return Decimal('0.00')
        if subtotal >= Decimal('499.00'):
            return Decimal('0.00')
        return Decimal('49.00')

    def get_free_shipping_remaining(self):
        subtotal = self.get_subtotal_price()
        threshold = Decimal('499.00')
        if subtotal >= threshold or subtotal == 0:
            return Decimal('0.00')
        return threshold - subtotal

    def get_free_shipping_progress(self):
        subtotal = self.get_subtotal_price()
        threshold = Decimal('499.00')
        if subtotal >= threshold:
            return 100
        return min(100, int((subtotal / threshold) * 100))

    def get_total_price(self):
        return max(Decimal('0.00'), self.get_subtotal_price() - self.get_discount_amount() + self.get_shipping_price())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        if 'coupon_id' in self.session:
            del self.session['coupon_id']
        self.save()
