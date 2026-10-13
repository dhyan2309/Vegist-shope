from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Category, Product, Review, NewsletterSubscriber


def home(request):
    categories = Category.objects.filter(is_featured=True)[:6]
    featured_products = Product.objects.filter(is_featured=True)[:8]
    trending_products = Product.objects.filter(is_trending=True)[:8]
    deal_products = Product.objects.filter(is_deal_of_the_day=True)
    # Prioritize deal product with bundle image for rich visual variety
    hero_deal = (
        deal_products.filter(image__icontains='deal_bundle').first()
        or deal_products.first()
        or featured_products.first()
    )
    best_sellers = Product.objects.order_by('-reviews_count')[:8]
    recent_reviews = Review.objects.select_related('product')[:6]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'trending_products': trending_products,
        'deal_products': deal_products,
        'hero_deal': hero_deal,
        'best_sellers': best_sellers,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'store/home.html', context)


from decimal import Decimal, InvalidOperation

def shop(request, category_slug=None):
    category = None
    products = Product.objects.all()

    # Category Filter
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        cat_id = request.GET.get('category')
        if cat_id:
            products = products.filter(category__id=cat_id)

    # Search Filter
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Price Filter
    min_price_raw = request.GET.get('min_price', '').strip()
    max_price_raw = request.GET.get('max_price', '').strip()

    min_clean = min_price_raw.replace('₹', '').replace(',', '').strip() if min_price_raw else ''
    max_clean = max_price_raw.replace('₹', '').replace(',', '').strip() if max_price_raw else ''

    parsed_min = None
    parsed_max = None

    if min_clean:
        try:
            parsed_min = Decimal(min_clean)
            if parsed_min < 0:
                parsed_min = Decimal('0')
        except (ValueError, InvalidOperation):
            parsed_min = None

    if max_clean:
        try:
            parsed_max = Decimal(max_clean)
            if parsed_max < 0:
                parsed_max = Decimal('0')
        except (ValueError, InvalidOperation):
            parsed_max = None

    # If both min and max provided and min > max, swap them automatically
    if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
        parsed_min, parsed_max = parsed_max, parsed_min

    if parsed_min is not None:
        products = products.filter(price__gte=parsed_min)
    if parsed_max is not None:
        products = products.filter(price__lte=parsed_max)

    # Organic only
    organic_only = request.GET.get('organic') == '1'
    if organic_only:
        products = products.filter(is_organic=True)

    # In-stock only
    in_stock_only = request.GET.get('in_stock') == '1'
    if in_stock_only:
        products = products.filter(stock__gt=0)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    # Pagination (12 items per page)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'products': page_obj,
        'total_count': products.count(),
        'query': query,
        'current_sort': sort,
        'selected_min': str(int(parsed_min)) if parsed_min is not None else '',
        'selected_max': str(int(parsed_max)) if parsed_max is not None else '',
        'organic_only': organic_only,
        'in_stock_only': in_stock_only,
        'has_price_filter': (parsed_min is not None or parsed_max is not None),
    }
    return render(request, 'store/shop.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        if name and email and comment:
            Review.objects.create(
                product=product,
                user_name=name,
                user_email=email,
                rating=rating,
                comment=comment
            )
            # Update product rating and reviews count
            all_reviews = product.reviews.all()
            avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
            product.rating = round(avg_rating, 1)
            product.reviews_count = len(all_reviews)
            product.save()

            messages.success(request, 'Thank you! Your verified review has been submitted.')
            return redirect('store:product_detail', slug=product.slug)

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


def quick_view_json(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'category': product.category.name,
        'category_url': product.category.get_absolute_url(),
        'price': str(product.price),
        'old_price': str(product.old_price) if product.old_price else None,
        'discount_percent': product.discount_percent,
        'unit': product.unit,
        'stock': product.stock,
        'in_stock': product.in_stock,
        'is_organic': product.is_organic,
        'rating': str(product.rating),
        'reviews_count': product.reviews_count,
        'short_description': product.short_description or product.description[:140] + '...',
        'image_url': product.image.url if product.image else '/static/images/cat_vegetables.jpg',
        'url': product.get_absolute_url(),
        'nutrition': product.nutrition_facts
    })


def deals_view(request):
    deal_products = Product.objects.filter(is_deal_of_the_day=True) | Product.objects.filter(old_price__isnull=False)
    deal_products = deal_products.distinct()
    return render(request, 'store/deals.html', {'deal_products': deal_products})


def about_view(request):
    return render(request, 'store/about.html')


def contact_view(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you! Your message has been sent to our customer care team.')
        return redirect('store:contact')
    return render(request, 'store/contact.html')


def recipes_view(request):
    return render(request, 'store/recipes.html')


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip().lower()
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Thank you for subscribing! Check your inbox for a 15% discount voucher.'})
        messages.success(request, 'Thank you for subscribing! Your 15% discount voucher is in your inbox.')
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))
