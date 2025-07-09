from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('servicio/<slug:servicio_slug>/', views.servicio_detail, name='servicio_detail'),
    path('servicio/<slug:servicio_slug>/<slug:service_slug>/', views.service_purchasable_detail, name='service_purchasable_detail'),
    

    
    # Carrito de compras (movido desde accounts)
    path('cart/', views.cart_view, name='cart'),
    path('cart/counter/', views.cart_counter, name='cart_counter'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout (movido desde accounts)
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('validate-user-data/', views.validate_user_data, name='validate_user_data'),
] 