from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from bakery.models import UserProfile, Order
from bakery.forms import UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.timezone import now
from datetime import timedelta

# Create your views here.
def orders(request):
    return render(request, 'user_dashboard/orders.html')

@login_required
def orders(request):
    # Fetch orders for the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Orders sorted by latest
    return render(request, 'user_dashboard/orders.html', {'orders': orders})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update the session to keep the user logged in after password change
            update_session_auth_hash(request, form.user)
            return redirect('user_dashboard:account_details')  # Redirect after password change
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'user_dashboard/password.html', {'form': form})

@login_required
def account_details(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard:account_details')  # Redirect after successful update
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'user_dashboard/account_details.html', {'form': form, 'profile': profile})

def coupons(request):
    return render(request, 'user_dashboard/coupons.html')