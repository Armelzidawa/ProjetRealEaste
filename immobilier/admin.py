"""
admin.py - Back-office Django
Valider / Rejeter les annonces, Gérer les biens
"""
from django.contrib import admin
from .models import Bien, Localisation, Annonce, Image, Contact, Favori


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    list_display  = ('titre', 'type_bien', 'categorie', 'prix', 'proprietaire', 'created_at')
    list_filter   = ('type_bien', 'categorie')
    search_fields = ('titre', 'proprietaire__username')
    inlines       = [ImageInline]


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display  = ('bien', 'statut', 'vues', 'datePublication')
    list_filter   = ('statut',)
    actions       = ['valider', 'rejeter']

    def valider(self, request, queryset):
        queryset.update(statut='validee')
        self.message_user(request, f"{queryset.count()} annonce(s) validée(s).")
    valider.short_description = "✅ Valider les annonces sélectionnées"

    def rejeter(self, request, queryset):
        queryset.update(statut='rejetee')
        self.message_user(request, f"{queryset.count()} annonce(s) rejetée(s).")
    rejeter.short_description = "❌ Rejeter les annonces sélectionnées"


@admin.register(Localisation)
class LocalisationAdmin(admin.ModelAdmin):
    list_display = ('ville', 'quartier', 'adresse')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'annonce', 'date_envoi', 'lu')
    list_filter  = ('lu',)


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'annonce', 'dateAjout')
