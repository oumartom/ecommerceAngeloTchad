from django import forms
from .models import Client, Order

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'phone_number', 'neighborhood', 'address_details']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+235 XX XX XX XX',
                'pattern': r'^\+235\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}$',
                'title': 'Format: +235 XX XX XX XX',
                'required': True
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre quartier',
                'required': True
            }),
            'address_details': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Détails de votre adresse (optionnel)',
                'rows': 3
            }),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'phone_number': 'Numéro de téléphone',
            'neighborhood': 'Quartier',
            'address_details': 'Détails de l\'adresse'
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notes ou instructions spéciales (optionnel)',
                'rows': 3
            }),
        }
        labels = {
            'notes': 'Notes'
        }

class OrderTrackingForm(forms.Form):
    order_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CMD-XXXXXXXX',
            'required': True
        }),
        label='Numéro de commande'
    )
    phone_number = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+235 XX XX XX XX',
            'pattern': r'^\+235\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}$',
            'title': 'Format: +235 XX XX XX XX',
            'required': True
        }),
        label='Numéro de téléphone'
    )

