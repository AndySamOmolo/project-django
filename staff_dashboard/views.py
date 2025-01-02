from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from bakery.models import Order, OrderItem
from bakery.models import BakeryItem
from django.contrib.auth.models import User
from django.db.models import Sum
from .forms import BakeryItemForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Check if the user is a staff member
def staff_check(user):
    return user.is_staff


# Manage Orders
@user_passes_test(staff_check)
def manage_orders(request):
    orders = Order.objects.filter(status='In Progress').prefetch_related('order_items__product').order_by('-created_at')
    return render(request, 'staff_dashboard/manage_orders.html', {'orders': orders})



@user_passes_test(staff_check)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        status = request.POST.get('status')
        order.status = status
        order.save()
        return redirect('staff_dashboard:manage_orders')
    return render(request, 'staff_dashboard/update_order_status.html', {'order': order})


# Update Bakery Items
@user_passes_test(staff_check)
def update_items(request):
    items = BakeryItem.objects.all()
    return render(request, 'staff_dashboard/update_items.html', {'items': items})


@user_passes_test(staff_check)
def edit_item(request, item_id):
    item = get_object_or_404(BakeryItem, id=item_id)
    if request.method == "POST":
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.available = request.POST.get('available') == 'on'
        item.save()
        return redirect('staff_dashboard:update_items')
    return render(request, 'staff_dashboard/edit_item.html', {'item': item})


# Generate Reports

@user_passes_test(staff_check)
def generate_reports(request):
    total_sales = Order.objects.filter(status='Completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.filter(status='In Progress').count()
    pending_orders = Order.objects.filter(status='Pending').count()
    bakery_items = BakeryItem.objects.all()
    top_items = (
        OrderItem.objects.filter(order__status='Completed') 
        .values('product__name') 
        .annotate(total_sold=Sum('quantity')) 
        .order_by('-total_sold')  
        [:5] 
    )
    return render(request, 'staff_dashboard/generate_reports.html', {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'top_items': top_items,
        'bakery_items' : bakery_items,
    })


# Manage Users
@user_passes_test(staff_check)
def manage_users(request):
    users = User.objects.filter(is_staff=False)  # Exclude staff accounts
    return render(request, 'staff_dashboard/manage_users.html', {'users': users})


@user_passes_test(staff_check)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('staff_dashboard:manage_users')
    return render(request, 'staff_dashboard/edit_user.html', {'user': user})

@login_required
def add_bakery_item(request):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-staff users

    if request.method == 'POST':
        form = BakeryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the new bakery item to the database
            return redirect('staff_dashboard:add_bakery_item')  # Redirect to the same page or another page after saving
    else:
        form = BakeryItemForm()

    return render(request, 'staff_dashboard/add_bakery_item.html', {'form': form})