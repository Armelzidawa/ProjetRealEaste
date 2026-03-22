"""
forms.py - Formulaires Django
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Bien, Localisation, Contact, TRANSACTION_CHOICES, TYPE_BIEN_CHOICES


class InscriptionForm(UserCreationForm):
    email      = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=50, label="Prénom")
    last_name  = forms.CharField(max_length=50, label="Nom")

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ConnexionForm(AuthenticationForm):
    pass


class BienForm(forms.ModelForm):
    # Champ supplémentaire : type de transaction (vente/location)
    categorie = forms.ChoiceField(choices=TRANSACTION_CHOICES, label="Transaction")

    class Meta:
        model  = Bien
        fields = ['titre', 'description', 'type_bien', 'categorie', 'prix', 'surface', 'nb_pieces', 'quartier']
        labels = {
            'titre':     'Titre de l\'annonce',
            'type_bien': 'Type de bien',
            'prix':      'Prix (FCFA)',
            'surface':   'Surface (m²)',
            'nb_pieces': 'Nombre de pièces',
            'quartier':  'Quartier',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class LocalisationForm(forms.ModelForm):
    class Meta:
        model  = Localisation
        fields = ['ville', 'quartier', 'adresse', 'latitude', 'longitude']
        labels = {
            'ville':    'Ville',
            'quartier': 'Quartier',
            'adresse':  'Adresse',
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model   = Contact
        fields  = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre message...'})}


class RechercheForm(forms.Form):
    q          = forms.CharField(required=False, label="Recherche")
    transaction = forms.ChoiceField(required=False, choices=[('', 'Tous')] + list(TRANSACTION_CHOICES))
    type_bien  = forms.ChoiceField(required=False, choices=[('', 'Tous')] + list(TYPE_BIEN_CHOICES))
    ville      = forms.CharField(required=False, label="Ville")
    prix_min   = forms.IntegerField(required=False, label="Prix min")
    prix_max   = forms.IntegerField(required=False, label="Prix max")
