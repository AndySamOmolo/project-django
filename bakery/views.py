from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomRegisterForm, CustomLoginForm
from django.contrib import messages
from .models import BakeryItem, Order, UserProfile
from cart.models import CartItem 
from django.core.paginator import Paginator
from .forms import UserProfileForm


# Create your views here.
def home(request):
    return render(request, 'bakery/home.html')

def products(request):
    items = BakeryItem.objects.all()
    paginator = Paginator(items, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'bakery/products.html', context)

def about(request):
    return render(request, 'bakery/about.html')

def contact(request):
    return render(request, 'bakery/contact.html')

def account(request):
    return render(request, 'bakery/account.html')

def cake_template(request, slug):
    item = get_object_or_404(BakeryItem, slug=slug)
    return render(request, 'bakery/cake-template.html', {'item' : item})

@login_required
def user_dashboard(request):  
    return render(request, 'user_dashboard/account_details.html')

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful.")
            return redirect('login')
    else:
        form = CustomRegisterForm()
    return render(request, 'bakery/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'bakery/login.html', {'form': form})