from django import forms

class OrderForm(forms.Form):
    item_name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    price = forms.DecimalField(min_value=0, max_digits=6, decimal_places=2)
    recipient = forms.CharField(max_length=100)

class ShopForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    image = forms.ImageField()