from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from store.models import Product
from .models import WishlistItem, Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not email or not password:
            messages.error(request, 'Please provide an email address and password.')
            return render(request, 'accounts/register.html')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, f'Welcome to Vegist Organic, {user.first_name or "Friend"}! Your account was created.')
        return redirect('store:home')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=login_input, password=password)
        if user is None:
            # Fallback in case username is different from email
            matched = User.objects.filter(Q(email__iexact=login_input) | Q(username__iexact=login_input)).first()
            if matched:
                user = authenticate(request, username=matched.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if not next_url or next_url == 'None':
                next_url = 'dashboard:home' if (user.is_staff or user.is_superuser) else 'store:home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'accounts/login.html')


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    step = 'identify'
    account_identifier = ''
    user_obj = None

    if request.method == 'POST':
        action = request.POST.get('action', 'find_account')

        if action == 'find_account':
            identifier = request.POST.get('identifier', '').strip()
            account_identifier = identifier
            if not identifier:
                messages.error(request, 'Please enter your registered email address or username.')
            else:
                user_obj = User.objects.filter(
                    Q(email__iexact=identifier) | Q(username__iexact=identifier)
                ).first()
                if user_obj:
                    step = 'reset'
                    messages.success(request, f'Account found for {user_obj.username}! Please enter your new password below.')
                else:
                    messages.error(request, f'No account found matching "{identifier}". Please verify and try again.')

        elif action == 'reset_password':
            identifier = request.POST.get('account_identifier', '').strip()
            account_identifier = identifier
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            user_obj = User.objects.filter(
                Q(email__iexact=identifier) | Q(username__iexact=identifier)
            ).first()

            if not user_obj:
                messages.error(request, 'Account not found. Please try again.')
                step = 'identify'
            elif len(new_password) < 4:
                step = 'reset'
                messages.error(request, 'Password must be at least 4 characters long.')
            elif new_password != confirm_password:
                step = 'reset'
                messages.error(request, 'Passwords do not match. Please re-enter.')
            else:
                user_obj.set_password(new_password)
                user_obj.save()
                login(request, user_obj)
                messages.success(request, f'Password updated successfully! Welcome back, {user_obj.first_name or user_obj.username}.')
                return redirect('store:home')

    context = {
        'step': step,
        'account_identifier': account_identifier,
        'user_obj': user_obj,
    }
    return render(request, 'accounts/forgot_password.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:home')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.country = request.POST.get('country', 'United States')
        profile.save()

        messages.success(request, 'Your profile details were updated.')
        return redirect('accounts:profile')

    orders = request.user.orders.all().order_by('-created_at') if hasattr(request.user, 'orders') else []
    return render(request, 'accounts/profile.html', {'profile': profile, 'orders': orders})


def wishlist_view(request):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        items = WishlistItem.objects.filter(user=request.user).select_related('product')
    else:
        items = WishlistItem.objects.filter(session_key=session_key).select_related('product')

    return render(request, 'accounts/wishlist.html', {'wishlist_items': items})


@require_POST
def toggle_wishlist(request, product_id):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        item = WishlistItem.objects.filter(user=request.user, product=product).first()
        if item:
            item.delete()
            added = False
            message = f'"{product.name}" removed from wishlist.'
        else:
            WishlistItem.objects.create(user=request.user, product=product)
            added = True
            message = f'"{product.name}" added to wishlist!'
        total_count = WishlistItem.objects.filter(user=request.user).count()
    else:
        item = WishlistItem.objects.filter(session_key=session_key, product=product).first()
        if item:
            item.delete()
            added = False
            message = f'"{product.name}" removed from wishlist.'
        else:
            WishlistItem.objects.create(session_key=session_key, product=product)
            added = True
            message = f'"{product.name}" added to wishlist!'
        total_count = WishlistItem.objects.filter(session_key=session_key).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'added': added,
            'message': message,
            'wishlist_count': total_count
        })

    messages.info(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))
