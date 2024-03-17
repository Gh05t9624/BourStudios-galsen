import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    rôle = forms.ChoiceField(choices=get_user_model().ROLES, initial='personnel')
    genre = forms.ChoiceField(choices=get_user_model().GENRE)
    
    class Meta:
        model = get_user_model()
        fields = ('rôle', 'genre', 'username', 'etablissement', 'email', 'password1', 'password2')
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        if len(username) > 150:
            raise forms.ValidationError("Le nom d'utilisateur ne peut pas dépasser 150 caractères.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cette adresse e-mail existe déjà.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
    
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
    
        return cleaned_data
