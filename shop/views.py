from django.http import request
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from .forms import CheckoutForm, CustomerRegistrationForm,CustomerLoginForm,AdminLoginForm
from .models import Cart, CartProduct, Category, Customer, ORDER_STATUS, Order, Product, Admin
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView, CreateView, ListView
from django.urls import reverse_lazy


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        user = request.user
        #assigning a customer to a cart
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if user.is_authenticated and user.customer:
                cart_obj.customer = user.customer
                cart_obj.save()

        return super().dispatch(request, *args, **kwargs)
    
# Create your views here.
class HomeView(EcomMixin,TemplateView):
    template_name="shop/index.html"
    # getting all items from the database
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # returns all item from the products schema
        context['product_list'] = Product.objects.all().order_by('-id') #showing the latest item
        # display categories
        context['list_cat'] = Category.objects.all()
        return context

# display items by category
class ProductView(EcomMixin,TemplateView):
    template_name="shop/products.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # display categories
        context['list_cat'] = Category.objects.all()
        return context

class ProductDetailView(EcomMixin,TemplateView):
    template_name="shop/product_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slugg = self.kwargs['slug']
        product = Product.objects.get(slug=slugg) #get will fetch only one item
        product.view_count +=1
        product.save()
        context['single_product'] = product
        return context
    
class AddToCartView(EcomMixin,TemplateView):
    template_name="shop/addto_cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product object for the db
        product_obj = Product.objects.get(id = product_id)
        # check whether the cart Exists or not using sessions
        cart_id = self.request.session.get('cart_id', None)

        if cart_id:
            # if the cart id exist we fetch the cart id
            cart_obj = Cart.objects.get(id=cart_id)
            #using the foriegn key in cart model
            product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            
            if product_in_cart.exists():
                # if items already exist in the cart
                cartproduct = product_in_cart.first()
                # increase the quantity
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total_amount += product_obj.selling_price
                cart_obj.save()
            else: 
                #if the item in the cart doesn't exist
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, 
                        rate=product_obj.selling_price,quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total_amount += product_obj.selling_price
                cart_obj.save()
        else:
            # or we create a new one
            cart_obj = Cart.objects.create(total_amount=0)
            # store the cart id in the sessions
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, 
                        rate=product_obj.selling_price,quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total_amount += product_obj.selling_price
            cart_obj.save()


        # check id the product already exist in the cart

        return context


class UserCartView(EcomMixin,TemplateView):
#sending cart data to the frontend
    template_name="shop/user_cart.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #first get the sessiion cart
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)

        else:
            cart_obj = None
        # display cart items
        context['cartitems'] = cart_obj

        return context

#increase, reduce and delete cart item
class ManageCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        # print("Managing cart items")
        cart_pdt_id = self.kwargs['cart_pdt_id']
        action = request.GET.get('action')
        cart_pdt_obj = CartProduct.objects.get(id=cart_pdt_id) #product object
        cart_item = cart_pdt_obj.cart #cart object
        
        if action == "inc":
            # increasing the quantity of an item in the cart
            cart_pdt_obj.quantity +=1
            cart_pdt_obj.subtotal += cart_pdt_obj.rate
            cart_pdt_obj.save()
            # 
            cart_item.total_amount += cart_pdt_obj.rate
            cart_item.save()
        elif action == "dcr":
            # removing item quantity from the cart
            cart_pdt_obj.quantity -=1
            cart_pdt_obj.subtotal -= cart_pdt_obj.rate
            cart_pdt_obj.save()
            # 
            cart_item.total_amount -= cart_pdt_obj.rate
            cart_item.save()
            # if the quantity is equal to 0, we delete the item from the cart
            if cart_pdt_obj.quantity == 0:
                cart_pdt_obj.delete()

        elif action == "del":
            # we're removing the subtotal from the total amount.
            cart_item.total_amount -= cart_pdt_obj.subtotal
            cart_item.save()
            cart_pdt_obj.delete() #delete the item(product obj) from the cart
        else:
            pass
        # print(cart_pdt_id, action)

        return redirect('shop:mycart')


class EmptyCartView(EcomMixin,View):

    def get(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id', None)
        if cart_id:
            cart_pdt_obj = Cart.objects.get(id=cart_id)
            cart_pdt_obj.cartproduct_set.all().delete()
            cart_pdt_obj.total_amount=0
            cart_pdt_obj.save()

        
        return redirect('shop:mycart')

class CheckoutView(EcomMixin,CreateView):
    template_name="shop/check_out.html"
    # adding the form class
    form_class = CheckoutForm
    # redirect after successful form submission
    success_url = reverse_lazy('shop:home')
    #to redirect a customer to login in before checking out
    # it's executed before the methods below it. also checks whether the user is logged in or not.
    def dispatch(self, request, *args, **kwargs):
        user = request.user #user currently logged in
        if user.is_authenticated and user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")


        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #first get the sessiion cart
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            # get the cart obj
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        # display cart items
        context['cartitems'] = cart_obj

        return context

# filling the rest of the field in the form.
    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            # the form instance that is saved into the database.
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total_amount
            form.instance.discount = 0
            form.instance.total = cart_obj.total_amount
            form.instance.order_status = "Order Recieved"

            del self.request.session['cart_id']

        else:

            return redirect('shop:home')

        return super().form_valid(form)



class CustomerRegistrationView(CreateView):
    template_name = "shop/customer_registration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('shop:home')

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")

        user = User.objects.create_user(username, email, password)

        form.instance.user = user
        login(self.request, user)

        return super().form_valid(form)
    
    #to override the success
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerLoginView(FormView):
    template_name = "shop/customer_login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy('shop:home')

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pwd = form.cleaned_data["password"]

        user_val = authenticate(username=uname, password=pwd) 
        if user_val is not None and Customer.objects.filter(user=user_val).exists():
            login(self.request, user_val)
        else:
            return render(self.request, self.template_name, 
            {"form": self.form_class, "error":"Invalid Credentials"})
        return super().form_valid(form)
    #to override the success
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("shop:home")

class CustomerProfileView(EcomMixin,TemplateView):
    template_name="shop/customer_profile.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user #user currently logged in
        if user.is_authenticated and Customer.objects.filter(user=user).exists():
            pass
        else:
            #redirect the user to profile after the login
            return redirect("/login/?next=/profile/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders'] = orders
        return context
    
# Template view can also be used.
class CustomerOrderDetailView(DetailView):
    template_name="shop/customer_order_details.html"
    model = Order
    context_object_name = "order_obj"
    # user must be logged in to view the order detail
    def dispatch(self, request, *args, **kwargs):
        user = request.user #user currently logged in
        if user.is_authenticated and Customer.objects.filter(user=user).exists():
            # obj to filter customer obj
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            # check if the customer is the owner of the order
            if request.user.customer != order.cart.customer:
                return redirect("shop:profile")

            #conditon to show orders of a specific customer
                     
        else:
            #redirect the user to profile after the login
            return redirect("/login/?next=/profile/")

        return super().dispatch(request, *args, **kwargs)
    

class AboutView(EcomMixin,TemplateView):
    template_name="shop/about.html"


class ContactView(EcomMixin,TemplateView):
    template_name="shop/contactus.html"
#================================Admin============
# Mixin to avoid repeating the dispatch method

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        user = request.user #user currently logged in
        if user.is_authenticated and Admin.objects.filter(user=user).exists():
            pass
        else:
            #redirect the user to profile after the login
            return redirect("/admin_login/")

        return super().dispatch(request, *args, **kwargs)

class AdminLoginView(FormView):
    template_name="admin/admin_login.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("shop:admin_home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pwd = form.cleaned_data["password"]

        user_val = authenticate(username=uname, password=pwd) 
        if user_val is not None and Admin.objects.filter(user=user_val).exists():
            login(self.request, user_val)
        else:
            return render(self.request, self.template_name, 
            {"form": self.form_class, "error":"Invalid Credentials"})
        return super().form_valid(form)

class AdminHomeView(AdminRequiredMixin, EcomMixin,TemplateView):
    template_name="admin/admin_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status="Order Recieved").order_by("-id")
        return context
    
class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name="admin/admin_order_detail.html"
    model = Order
    context_object_name = "order_obj"

    # gettingthe options
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context
    


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name="admin/admin_order_list.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "all_orders"

class AdminLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("shop:admin_login")

class AdminOrderStatusChangeView(View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
# change the order object
        order_obj.order_status = new_status
        order_obj.save()

        return redirect(reverse_lazy("shop:admin_order_detail",kwargs={"pk":order_id}))