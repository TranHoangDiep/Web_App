from django.urls import path
from cart import views


app_name = 'cart'
urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('cart-remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
]
