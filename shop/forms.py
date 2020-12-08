from django import forms
from .models import Customer, Order
from django.contrib.auth.models import User
# angle form
class CheckoutForm(forms.ModelForm):
    class Meta:
        model= Order
        # list of fields that you want to show on the form
        fields = ["ordered_by", "shipping_address","mobile", "email"]

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())
    class Meta:
        model = Customer
        fields = ["username", "password","email","full_name", "address"]
# username validation
    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Customer with this username already Exists")

        return uname

class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
