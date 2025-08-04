# from django import forms
# from .models import Client, Order

# class ClientForm(forms.ModelForm):
#     class Meta:
#         model = Client
#         fields = ['first_name', 'last_name', 'phone_number', 'neighborhood', 'address_details']
#         widgets = {
#             'first_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Votre prénom',
#                 'required': True
#             }),
#             'last_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Votre nom',
#                 'required': True
#             }),
#             'phone_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': '+235 XX XX XX XX ou 6X XX XX XX',
#                 'title': 'Format accepté: +235 XX XX XX XX ou 6X XX XX XX (8 chiffres)',
#                 'required': True
#             }),
#             'neighborhood': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Votre quartier',
#                 'required': True
#             }),
#             'address_details': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Détails de votre adresse (optionnel)',
#                 'rows': 3
#             }),
#         }
#         labels = {
#             'first_name': 'Prénom',
#             'last_name': 'Nom',
#             'phone_number': 'Numéro de téléphone',
#             'neighborhood': 'Quartier',
#             'address_details': 'Détails de l\'adresse'
#         }

#     def clean_phone_number(self):
#         phone = self.cleaned_data.get('phone_number', '')
        
#         # Nettoyage: ne garder que les chiffres
#         cleaned = ''.join(c for c in phone if c.isdigit())
        
#         # Validation de base
#         if len(cleaned) < 8:
#             raise forms.ValidationError("Le numéro doit contenir 8 chiffres")
        
#         if not cleaned.startswith('6'):
#             raise forms.ValidationError("Le numéro doit commencer par 6")
        
#         # Formatage standard
#         formatted = f"+235 {cleaned[:2]} {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:8]}"
#         return formatted

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['notes']
#         widgets = {
#             'notes': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Notes ou instructions spéciales (optionnel)',
#                 'rows': 3
#             }),
#         }
#         labels = {
#             'notes': 'Notes'
#         }

# class OrderTrackingForm(forms.Form):
#     order_number = forms.CharField(
#         max_length=20,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'CMD-XXXXXXXX',
#             'required': True
#         }),
#         label='Numéro de commande'
#     )
#     phone_number = forms.CharField(
#         max_length=20,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': '+235 XX XX XX XX ou 6X XX XX XX',
#             'title': 'Format accepté: +235 XX XX XX XX ou 6X XX XX XX (8 chiffres)',
#             'required': True
#         }),
#         label='Numéro de téléphone'
#     )

#     def clean_phone_number(self):
#         phone = self.cleaned_data.get('phone_number', '')
        
#         # Nettoyage radical (ne garde que les chiffres)
#         cleaned = ''.join(c for c in phone if c.isdigit())
        
#         # Validation 1: Numéro local (8 chiffres commençant par 6)
#         if len(cleaned) == 8 and cleaned.startswith('6'):
#             return '+235 ' + ' '.join([cleaned[i:i+2] for i in range(0, 8, 2)])
        
#         # Validation 2: Numéro avec indicatif (2356XXXXXXXX)
#         elif len(cleaned) == 12 and cleaned.startswith('2356'):
#             return '+235 ' + ' '.join([cleaned[4:6], cleaned[6:8], cleaned[8:10], cleaned[10:]])
        
#         # Validation 3: Numéro avec +235 (supprime le + pour compter)
#         elif len(cleaned) == 11 and cleaned.startswith('2356'):
#             return '+235 ' + ' '.join([cleaned[4:6], cleaned[6:8], cleaned[8:10], cleaned[10:]])
        
#         # Si aucun cas ne correspond
#         raise forms.ValidationError(
#             "Format invalide. Exemples valides :\n"
#             "- +235 6X XX XX XX\n"
#             "- 6X XX XX XX\n"
#             "- 6XXXXXXXX"
#         )
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
            'placeholder': '+235 XX XX XX XX ou XX XX XX XX',
            'pattern': r'^(\+235\s?)?6\d(\s?\d{2}){3}$',
            'title': 'Format accepté : +235 XX XX XX XX ou XX XX XX XX',
            'required': True
        }),
        label='Numéro de téléphone'
    )


def clean_phone_number(self):
    number = self.cleaned_data['phone_number'].replace(' ', '')
        
    if number.startswith('+235'):
        number = number[4:]
    elif number.startswith('00235'):
        number = number[5:]
        
    if len(number) != 8 or not number.isdigit():
        raise forms.ValidationError("Numéro invalide. Doit contenir 8 chiffres après l'indicatif.")
        
    return '+235 ' + ' '.join([number[i:i+2] for i in range(0, 8, 2)])

