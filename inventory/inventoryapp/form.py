from .models import *
from django.forms import ModelForm, TextInput
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError




class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'parent': TextInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'address': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Company Name',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
        }
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'price': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(attrs={'class': 'form-control'}),
            'category': TextInput(attrs={'class': 'form-control'}),
            'supplier': TextInput(attrs={'class': 'form-control'}),
            'quantity_in_stock': TextInput(attrs={'class': 'form-control'}),
           'sku': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Product Name',
            'price': 'Price',
            'description': 'Description',
            'category': 'Category',
           'supplier': 'Supplier',
            'quantity_in_stock': 'Quantity in Stock',
           'sku': 'SKU',
            'location': 'Location',
        }
class InventoryTransactionForm(ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        widgets = {
            'product': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
            'transaction_type': TextInput(attrs={'class': 'form-control'}),
            'notes': TextInput(attrs={'class': 'form-control'}),
           'related_order': TextInput(attrs={'class': 'form-control'}),
        }
class InventoryItemForm(ModelForm):
    class Meta:
        model = InventoryItem
        fields = '__all__'
        widgets = {
            'product': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product': 'Product',
            'location': 'Location',
            'quantity_in_stock': 'Quantity in Stock',

        }

class InventoryReportForm(ModelForm):
    class Meta:
        model = InventoryReport
        fields = '__all__'
        widgets = {
            'product': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
            'from_date': TextInput(attrs={'class': 'form-control'}),
            'to_date': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product': 'Product',
            'location': 'Location',
            'from_date': 'From Date',
            'to_date': 'To Date',
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    terms = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "terms")

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise ValidationError("You must accept the terms and conditions.")
        return terms