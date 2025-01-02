from django.db import models
from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.CharField(max_length=40, null=True, blank=True)  # For anonymous users
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart (Session: {self.session})"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())  # Ensuring proper method call


class CartItem(models.Model):
    SIZE_CHOICES = [
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('bakery.BakeryItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Default quantity is 1
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='Medium')
    custom_message = models.CharField(max_length=255, null=True, blank=True)
    toppings = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Stores price at the time of adding
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.size}) in {self.cart}"  

    def get_total_price(self):
        return self.quantity * self.price
