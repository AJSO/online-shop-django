from django.urls import path
from .views import *

app_name= 'shop'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('products/', ProductView.as_view(), name='all_products'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='products_detail'),

    path('add_to_art_<int:pro_id>/', AddToCartView.as_view(), name='addtocart'),
    path('user_cart/', UserCartView.as_view(), name='mycart'),
    path('manage_cart/<int:cart_pdt_id>/', ManageCartView.as_view(), name='managecart'),
    path('empty_cart/', EmptyCartView.as_view(), name='emptycart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('register/', CustomerRegistrationView.as_view(), name='newUser'),
    path('login/', CustomerLoginView.as_view(), name='login'),
    path('logout/', CustomerLogoutView.as_view(), name='logout'),


    path('profile/', CustomerProfileView.as_view(), name='profile'),
    path('profile/order-<int:pk>/', CustomerOrderDetailView.as_view(), name='order_detail'),
]
