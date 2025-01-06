from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from bakery.models import BakeryItem
from django.contrib.auth.models import User
from .forms import BakeryItemForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from bakery.models import Order, OrderItem, BakeryItem
from django.db.models import Sum
from django.contrib.auth.hashers import make_password


def admin_check(user):
    return user.is_superuser


@user_passes_test(admin_check)
def generate_pdf_report(request):
    # Fetch data for the report
    total_sales = Order.objects.filter(status='Completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.filter(status='In Progress').count()
    pending_orders = Order.objects.filter(status='Pending').count()
    top_items = (
        OrderItem.objects.filter(order__status='Completed')
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'top_items': top_items,
    }

    # Render the template to a string
    html = render_to_string('admin_dashboard/generate_reports.html', context)

    # Create a BytesIO buffer to store the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF', content_type='text/plain')

    # Serve the PDF as a response
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response


@user_passes_test(admin_check)
def manage_users(request):
    users = User.objects.filter(is_staff=False)  # Exclude staff accounts
    return render(request, 'admin_dashboard/manage_users.html', {'users': users})

@user_passes_test(admin_check)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('staff_dashboard:manage_users')
    return render(request, 'admin_dashboard/edit_user.html', {'user': user})

@user_passes_test(admin_check)
def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_staff = request.POST.get('is_staff') == 'on'

        # Validate the passwords match
        if password != confirm_password:
            return render(request, 'admin_dashboard/add_user.html', {
                'error': "Passwords do not match."
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'admin_dashboard/add_user.html', {
                'error': "Username already exists."
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'admin_dashboard/add_user.html', {
                'error': "Email already in use."
            })

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=is_staff
        )
        user.save()
        return redirect('admin_dashboard:manage_users')  # Redirect to user management page

    return render(request, 'admin_dashboard/add_user.html')


@login_required
@user_passes_test(admin_check)
def add_bakery_item(request):
    if request.method == 'POST':
        form = BakeryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  
            return redirect('admin_dashboard:add_bakery_item') 
    else:
        form = BakeryItemForm()

    return render(request, 'admin_dashboard/add_bakery_item.html', {'form': form})


