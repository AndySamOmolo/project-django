from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem, Cart
from bakery.models import BakeryItem
from decimal import Decimal

def product_list(request):
    return render(request, 'bakery/products.html')
                  
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
    else:
        cart_items = CartItem.objects.filter(cart__session=request.session.session_key)

    total_price = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, item_id):
    product = get_object_or_404(BakeryItem, id=item_id)

    # Handle authenticated user
    if request.user.is_authenticated:
        # Get or create cart for logged-in user
        cart, created = Cart.objects.get_or_create(user=request.user, defaults={'session': None})
    else:
        # Handle anonymous user
        session_key = request.session.session_key
        if not session_key:
            request.session.create()  # Create a new session if it doesn't exist
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session=session_key, user=None)

    if request.method == "POST":
        # Extract additional data from the form
        size = request.POST.get('size', 'Medium')  # Default to 'Medium' if size is not provided
        toppings = request.POST.get('toppings', '')  # Default to an empty string if not provided
        custom_message = request.POST.get('message', '')  # Default to an empty string
        quantity = int(request.POST.get('quantity', 1))  # Default to 1

        # Create or update cart item with additional fields
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            toppings=toppings,
            custom_message=custom_message,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:
            # If the item already exists in the cart, update quantity
            cart_item.quantity += quantity
            cart_item.save(update_fields=['quantity'])

    return redirect('cart:view_cart')



def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart:view_cart')


def update_quantity(request, item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        cart_item.quantity = max(1, quantity)  # Ensure quantity is at least 1
        cart_item.save(update_fields=['quantity'])
    return redirect('cart:view_cart')



