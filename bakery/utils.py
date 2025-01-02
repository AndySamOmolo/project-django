from .models import Order, OrderItem
from cart.models import Cart, CartItem
from bakery.models import BakeryItem

def create_orders_from_cart(user, session=None):
    try:
        # Get the user's cart or handle anonymous user case
        cart = Cart.objects.get(user=user) if user.is_authenticated else Cart.objects.filter(session=session).first()

        if cart and cart.items.exists():
            # Loop through each item in the cart and create an order for each
            for item in cart.items.all():
                if not item.product:
                    print(f"CartItem {item.id} is missing a product!")
                    continue  # Skip creating an order item if no product exists

                if item.quantity is None or item.quantity <= 0:
                    # Optionally set a default or handle the issue
                    item.quantity = 1  # Default quantity if invalid
                    print(f"Default quantity for {item.product.name}: {item.quantity}")

                # Create an order entry without the product (we'll create OrderItem later)
                order = Order.objects.create(
                    user=user if user.is_authenticated else None,
                    cart=cart,
                    status='Pending',
                    total_price=item.get_total_price(),  # Total price will be calculated later
                )
                print(f"Order created for cart #{cart.id}.")

                # Create OrderItems for each cart item
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.get_total_price(),
                )
                print(f"OrderItem created for {item.product.name} with quantity {item.quantity}")
            
            # Optionally, clear cart items after successful order transfer
            cart.items.all().delete()
            return True  # Success
        else:
            print("No items in the cart or cart not found.")
            return False  # No items in the cart
    except Exception as e:
        print(f"Error creating orders from cart: {e}")
        return False  # Error
