from .models import Category


def categories_context(request):
    categories = Category.objects.all().prefetch_related('products')
    return {
        'all_categories': categories,
        'featured_categories': categories.filter(is_featured=True)[:8],
    }
