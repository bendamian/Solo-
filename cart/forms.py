from django import forms


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
