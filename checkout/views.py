from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils import initiate_stk_push
from bakery.utils import create_orders_from_cart
import json
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from bakery.models import Order, UserProfile, OrderItem
from cart.models import Cart, CartItem


def get_details(request):
    user = request.user
    if user.is_authenticated:
        cart = Cart.objects.get(user=user)
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session=session_key).first()

    if cart:
        # Create the order
        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            cart=cart,
            status='Pending',
        )

        # Create OrderItems for each item in the cart
        total_price = Decimal('0.00')  # Initialize total price
        for item in cart.items.all():  # Assuming Cart has a related field 'items'
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,  # Assuming cart item has a 'product' field
                quantity=item.quantity,
                total_price=item.product.price * item.quantity
            )
            total_price += order_item.total_price  # Add the item's total price to the order's total

        # Update order's total price (you can add this field to the Order model if needed)
        order.total_price = total_price
        order.save()

        return render(request, 'checkout/payment_form.html', {'order': order, 'total_price': total_price})
    else:
        return HttpResponse("No cart found.", status=400)


@login_required
def initiate_payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        phone_number = request.POST.get('phone_number')

        if not order_id:
            return render(request, 'checkout/payment_error.html', {'error': 'Order ID is missing.'})

        if not phone_number:
            return render(request, 'checkout/payment_error.html', {'error': 'Phone number is required.'})

        try:
            # Get the order
            order = Order.objects.get(id=order_id)
            total_price = order.total_price

            # Ensure valid amount
            if total_price <= 0:
                return render(request, 'checkout/payment_error.html', {'error': 'Invalid total price.'})

            # Initiate the STK Push
            response = initiate_stk_push(phone_number, total_price, f"Order-{order_id}", "Checkout Payment")

            # Check if the initiation was successful
            if 'error' in response:
                return render(request, 'checkout/payment_error.html', {'error': response.get('error')})

            # Show a "Payment Pending" page to the user
            return render(request, 'checkout/payment_pending.html', {'order': order, 'response': response})

        except Order.DoesNotExist:
            return render(request, 'checkout/payment_error.html', {'error': 'Order not found'})

    return redirect('checkout:get_details')






@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body.decode('utf-8'))
            print("Mpesa Callback Data:", data)

            # Extract the relevant details from the callback response
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            order_id = stk_callback.get('OrderID')  # Ensure order_id is passed in callback

            if not result_code or not result_desc:
                return render(request, 'checkout/payment_error.html', {'error': "Missing necessary data in the callback"})

            # Handle payment result
            if result_code == 0:
                # Payment was successful
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = 'In Progress' 
                    order.save()

                    # Clear the cart after successful payment
                    cart = Cart.objects.get(user=order.user) if order.user else None
                    if cart:
                        cart.items.all().delete()

                    # Create the orders from the cart after payment is confirmed
                    if create_orders_from_cart(order.user):
                        return render(request, 'checkout/payment_success.html')  # Success page
                    else:
                        return render(request, 'checkout/payment_error.html', {'error': 'No items in cart to process.'})
                except Order.DoesNotExist:
                    return render(request, 'checkout/payment_error.html', {'error': f"Order with ID {order_id} not found"})

            elif result_code == 1032:
                # User canceled the request
                return render(request, 'checkout/payment_error.html', {'error': "Payment was canceled by the user."})

            # Handle other failure cases
            elif result_code != 0:
                return render(request, 'checkout/payment_error.html', {'error': f"Payment failed: {result_desc}."})

        except json.JSONDecodeError:
            return render(request, 'checkout/payment_error.html', {'error': "Invalid JSON data received from Mpesa"})
        except Exception as e:
            print(f"Error processing callback: {str(e)}")
            return render(request, 'checkout/payment_error.html', {'error': f"Error processing callback: {str(e)}"})

    else:
        return render(request, 'checkout/payment_error.html', {'error': "Invalid request method. Expected POST."})
