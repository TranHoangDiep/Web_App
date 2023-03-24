from django.urls import path
from store import views


app_name = 'store'
urlpatterns = [
    path('', views.index, name='index'),
    path('subcategory/<int:pk>/', views.subcategory, name='subcategory'),
    path('contact/', views.contact, name='contact'),
    path('user/', views.demo_user, name='user'),
    path('logout-user/', views.logout_user, name='logout_user'),
    path('products-service/', views.products_service, name='products_service'),
    path('products-service/<int:pk>/', views.product_service, name='product_service'),
    path('search/', views.search, name='search'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]
