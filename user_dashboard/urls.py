from django.urls import path
from . import views

app_name = 'user_dashboard'

urlpatterns = [
    path('orders/', views.orders, name='orders'),
    path('account_details', views.account_details, name='account_details'),
    path('coupons', views.coupons, name='coupons'),
    path('change_password/', views.change_password, name='change_password'),
]