from django.contrib import admin
from .models import Category, BakeryItem, Order, OrderItem


class BakeryItemInline(admin.TabularInline):  # Allows editing items within Category
    model = BakeryItem
    extra = 1  # Number of empty forms to show for new items


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
    inlines = [BakeryItemInline]  # Include BakeryItem editing in Category admin


@admin.register(BakeryItem)
class BakeryItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category', 'formatted_price', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name', 'description', 'ingredients')
    ordering = ('-price', 'name')  

    def formatted_price(self, obj):
        return f"Kshs {obj.price:.2f}"
    formatted_price.short_description = 'Price'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra empty forms will be shown by default

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_total_price', 'status', 'created_at')  # Use a method for total price
    readonly_fields = ('get_total_price',)  # Make total price read-only in the form
    inlines = [OrderItemInline]  # Add OrderItemInline to display items in the order

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.order_items.all())
    get_total_price.short_description = 'Total Price'  # Optional: Label for the column

admin.site.register(Order, OrderAdmin)