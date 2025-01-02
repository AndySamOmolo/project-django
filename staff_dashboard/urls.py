from django.urls import path
from . import views

app_name = 'staff_dashboard'

urlpatterns = [
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('update-items/', views.update_items, name='update_items'),
    path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('generate-reports/', views.generate_reports, name='generate_reports'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('add-bakery-item/', views.add_bakery_item, name='add_bakery_item'),
]
