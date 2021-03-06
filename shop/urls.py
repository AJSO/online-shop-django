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

    path('admin_login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin_all_orders/', AdminOrderListView.as_view(), name='all_orders'),
    path('admin_home/', AdminHomeView.as_view(), name='admin_home'),
    path('admin_order/<int:pk>/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin_logout/', AdminLogoutView.as_view(), name='admin_logout'),


    path('admin_order_<int:pk>-change/', AdminOrderStatusChangeView.as_view(), name='order_status_change'),


    path('search/', SearchView.as_view(), name='search'),
]
