from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import AgentProfile

class AgentCreationForm(UserCreationForm):
    """Formulaire pour créer un nouvel agent"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    role = forms.ChoiceField(
        choices=AgentProfile.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+235 XX XX XX XX'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Créer ou mettre à jour le profil agent
            agent_profile, created = AgentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phone_number': self.cleaned_data['phone_number'],
                    'is_active': True
                }
            )
            if not created:
                agent_profile.role = self.cleaned_data['role']
                agent_profile.phone_number = self.cleaned_data['phone_number']
                agent_profile.save()
        
        return user

class AgentUpdateForm(forms.ModelForm):
    """Formulaire pour modifier un agent existant"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = AgentProfile
        fields = ('role', 'phone_number', 'is_active')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+235 XX XX XX XX'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        agent_profile = super().save(commit=False)
        
        # Mettre à jour les informations de l'utilisateur
        user = agent_profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            agent_profile.save()
        
        return agent_profile

