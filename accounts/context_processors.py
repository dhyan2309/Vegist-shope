from .models import WishlistItem


def wishlist_context(request):
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
    elif request.session.session_key:
        wishlist_ids = list(WishlistItem.objects.filter(session_key=request.session.session_key).values_list('product_id', flat=True))
    
    return {
        'wishlist_count': len(wishlist_ids),
        'wishlist_ids': wishlist_ids
    }
