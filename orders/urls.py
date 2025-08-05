from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-d/<int:product_id>', views.checkoutd, name='checkoutd'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('tracking/', views.order_tracking, name='order_tracking'),
    

]

