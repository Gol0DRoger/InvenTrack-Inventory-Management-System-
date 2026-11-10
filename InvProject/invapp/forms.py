import re
from django import forms
from .models import Product

class productForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        labels = {
            'product_id': 'Product ID',
            'name': 'Name',
            'sku': 'SKU',
            'price': 'Price',
            'quantity': 'Quantity',
            'supplier': 'Supplier',
        }
        widgets = {
            'product_id': forms.NumberInput(
                attrs={'placeholder': 'e.g 1', 'class': 'form-control'}
            ),
            'name': forms.TextInput(
                attrs={'placeholder': 'e.g shirt', 'class': 'form-control'}
            ),
            'sku': forms.TextInput(
                attrs={'placeholder': 'e.g ABC-1234', 'class': 'form-control'}
            ),
            'price': forms.NumberInput(
                attrs={'placeholder': 'e.g 20.00', 'class': 'form-control'}
            ),
            'quantity': forms.NumberInput(
                attrs={'placeholder': 'e.g 10', 'class': 'form-control'}
            ),
            'supplier': forms.TextInput(
                attrs={'placeholder': 'e.g XYZ corp', 'class': 'form-control'}
            ),
        }

    def clean_sku(self):
        sku = self.cleaned_data.get('sku', '').strip().upper()
        if not re.match(r'^[A-Z]{3}-\d{4}$', sku):
            raise forms.ValidationError('SKU must be in the format ABC-1234 (3 uppercase letters, hyphen, 4 digits).')
        return sku
