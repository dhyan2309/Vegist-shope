from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, Q
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from store.models import Product, Category, Review
from orders.models import Order, OrderItem
from cart.models import Coupon
from accounts.models import Profile


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


admin_required = user_passes_test(is_admin, login_url='/accounts/login/?next=/dashboard/')


@admin_required
def dashboard_home(request):
    total_revenue = Order.objects.filter(
        Q(is_paid=True) | Q(status__in=['processing', 'shipped', 'delivered'])
    ).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')

    total_orders = Order.objects.count()
    pending_orders_count = Order.objects.filter(status='pending').count()
    delivered_orders_count = Order.objects.filter(status='delivered').count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=15).order_by('stock')
    low_stock_count = low_stock_products.count()
    total_customers = User.objects.filter(is_staff=False).count()
    total_categories = Category.objects.count()

    recent_orders = Order.objects.all().order_by('-created_at')[:8]
    recent_reviews = Review.objects.all().order_by('-created_at')[:5]
    top_categories = Category.objects.annotate(prod_count=Count('products')).order_by('-prod_count')[:6]

    context = {
        'active_menu': 'dashboard',
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5],
        'total_customers': total_customers,
        'total_categories': total_categories,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'top_categories': top_categories,
    }
    return render(request, 'dashboard/index.html', context)


# ======================== PRODUCT MANAGEMENT ========================

@admin_required
def products_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')

    products = Product.objects.select_related('category').all().order_by('-created_at')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if stock_filter == 'low':
        products = products.filter(stock__lte=15, stock__gt=0)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    elif stock_filter == 'in':
        products = products.filter(stock__gt=0)

    categories = Category.objects.all().order_by('name')

    # Stock counts for quick status filtering
    stock_counts = {
        'all': Product.objects.count(),
        'in': Product.objects.filter(stock__gt=0).count(),
        'low': Product.objects.filter(stock__lte=15, stock__gt=0).count(),
        'out': Product.objects.filter(stock=0).count(),
    }

    context = {
        'active_menu': 'products',
        'products': products,
        'categories': categories,
        'selected_q': query,
        'selected_category': category_id,
        'selected_stock': stock_filter,
        'total_count': products.count(),
        'stock_counts': stock_counts,
    }
    return render(request, 'dashboard/products.html', context)


@admin_required
def product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price', '0')
        old_price = request.POST.get('old_price') or None
        unit = request.POST.get('unit', '1 kg').strip()
        stock = request.POST.get('stock', '50')
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        is_organic = request.POST.get('is_organic') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        is_trending = request.POST.get('is_trending') == 'on'
        is_deal_of_the_day = request.POST.get('is_deal_of_the_day') == 'on'
        image = request.FILES.get('image')

        if not name or not category_id or not price:
            messages.error(request, 'Please fill in all required fields (Name, Category, Price).')
        else:
            category = get_object_or_404(Category, id=category_id)
            slug = slugify(name)
            # Ensure unique slug
            unique_slug = slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slug}-{counter}"
                counter += 1

            product = Product.objects.create(
                category=category,
                name=name,
                slug=unique_slug,
                price=Decimal(price),
                old_price=Decimal(old_price) if old_price else None,
                unit=unit,
                stock=int(stock),
                short_description=short_description,
                description=description,
                is_organic=is_organic,
                is_featured=is_featured,
                is_trending=is_trending,
                is_deal_of_the_day=is_deal_of_the_day,
            )
            if image:
                product.image = image
                product.save()

            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('dashboard:products_list')

    return render(request, 'dashboard/product_form.html', {
        'active_menu': 'products',
        'categories': categories,
        'action': 'Add',
    })


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price', '0')
        old_price = request.POST.get('old_price') or None
        unit = request.POST.get('unit', '1 kg').strip()
        stock = request.POST.get('stock', '50')
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        is_organic = request.POST.get('is_organic') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        is_trending = request.POST.get('is_trending') == 'on'
        is_deal_of_the_day = request.POST.get('is_deal_of_the_day') == 'on'
        image = request.FILES.get('image')

        if not name or not category_id or not price:
            messages.error(request, 'Please fill in all required fields.')
        else:
            product.name = name
            product.category = get_object_or_404(Category, id=category_id)
            product.price = Decimal(price)
            product.old_price = Decimal(old_price) if old_price else None
            product.unit = unit
            product.stock = int(stock)
            product.short_description = short_description
            product.description = description
            product.is_organic = is_organic
            product.is_featured = is_featured
            product.is_trending = is_trending
            product.is_deal_of_the_day = is_deal_of_the_day

            if image:
                product.image = image

            product.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('dashboard:products_list')

    return render(request, 'dashboard/product_form.html', {
        'active_menu': 'products',
        'categories': categories,
        'product': product,
        'action': 'Edit',
    })


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" was removed.')
    return redirect('dashboard:products_list')


# ======================== ORDER MANAGEMENT ========================

@admin_required
def orders_list(request):
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    orders = Order.objects.prefetch_related('items').all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    status_counts = {
        'all': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'processing': Order.objects.filter(status='processing').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }

    context = {
        'active_menu': 'orders',
        'orders': orders,
        'selected_status': status_filter,
        'selected_q': query,
        'total_count': orders.count(),
        'status_choices': Order.STATUS_CHOICES,
        'status_counts': status_counts,
    }
    return render(request, 'dashboard/orders.html', context)


@admin_required
def order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
        if 'set_paid' in request.POST:
            order.is_paid = (request.POST.get('set_paid') == '1')
        elif 'is_paid' in request.POST:
            order.is_paid = (request.POST.get('is_paid') in ['on', 'true', '1'])
        order.save()
        messages.success(request, f'Order #{order.order_number} updated: Status is "{order.get_status_display()}", Payment is {"Paid" if order.is_paid else "Unpaid"}.')
        return redirect('dashboard:order_detail', order_number=order.order_number)

    return render(request, 'dashboard/order_detail.html', {
        'active_menu': 'orders',
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })


# ======================== CATEGORY MANAGEMENT ========================

@admin_required
def categories_list(request):
    categories = Category.objects.annotate(prod_count=Count('products')).order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', 'ri-plant-line').strip()
        is_featured = request.POST.get('is_featured') == 'on'
        image = request.FILES.get('image')

        if not name:
            messages.error(request, 'Category name is required.')
        else:
            slug = slugify(name)
            unique_slug = slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slug}-{counter}"
                counter += 1

            cat = Category.objects.create(
                name=name,
                slug=unique_slug,
                icon=icon,
                is_featured=is_featured
            )
            if image:
                cat.image = image
                cat.save()

            messages.success(request, f'Category "{cat.name}" added successfully!')
            return redirect('dashboard:categories_list')

    return render(request, 'dashboard/categories.html', {
        'active_menu': 'categories',
        'categories': categories,
    })


@admin_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Category "{name}" removed.')
    return redirect('dashboard:categories_list')


# ======================== CUSTOMER MANAGEMENT ========================

@admin_required
def customers_list(request):
    query = request.GET.get('q', '').strip()
    customers = User.objects.filter(is_staff=False).select_related('profile').annotate(
        order_count=Count('orders')
    ).order_by('-date_joined')

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    return render(request, 'dashboard/customers.html', {
        'active_menu': 'customers',
        'customers': customers,
        'selected_q': query,
        'total_count': customers.count(),
    })


# ======================== COUPON MANAGEMENT ========================

@admin_required
def coupons_list(request):
    coupons = Coupon.objects.all().order_by('-id')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        discount_percent = request.POST.get('discount_percent', '10')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        active = request.POST.get('active') == 'on'

        if not code or not discount_percent:
            messages.error(request, 'Code and Discount % are required.')
        elif Coupon.objects.filter(code=code).exists():
            messages.error(request, f'Coupon code "{code}" already exists!')
        else:
            Coupon.objects.create(
                code=code,
                discount_percent=int(discount_percent),
                valid_from=valid_from or timezone.now(),
                valid_to=valid_to or (timezone.now() + timedelta(days=90)),
                active=active
            )
            messages.success(request, f'Coupon "{code}" created!')
            return redirect('dashboard:coupons_list')

    return render(request, 'dashboard/coupons.html', {
        'active_menu': 'coupons',
        'coupons': coupons,
    })


@admin_required
def coupon_toggle(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.active = not coupon.active
        coupon.save()
        status_text = 'activated' if coupon.active else 'deactivated'
        messages.success(request, f'Coupon {coupon.code} was {status_text}.')
    return redirect('dashboard:coupons_list')


# ======================== REVIEWS MANAGEMENT ========================

@admin_required
def reviews_list(request):
    reviews = Review.objects.select_related('product').all().order_by('-created_at')
    return render(request, 'dashboard/reviews.html', {
        'active_menu': 'reviews',
        'reviews': reviews,
    })


@admin_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review was deleted.')
    return redirect('dashboard:reviews_list')
