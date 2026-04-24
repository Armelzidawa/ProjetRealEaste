"""
urls.py - Toutes les URLs de l'application immobilier
"""
from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.home,           name='home'),
    path('annonce/<int:pk>/',       views.detail_annonce, name='detail_annonce'),

    path('inscription/',            views.inscription,    name='inscription'),
    path('connexion/',              views.connexion,      name='connexion'),
    path('deconnexion/',            views.deconnexion,    name='deconnexion'),
    
    path('tableau-de-bord/',        views.tableauBord,    name='tableauBord'),
    path('favoris/',                views.favoris,        name='favoris'),
    path('mes-messages/',           views.mes_messages,   name='mes_messages'),
    path('logement/',               views.logement,       name='logement'),

    path('ajouter/',                views.ajouter,        name='ajouter'),
    path('modifier/<int:pk>/',      views.modifier,       name='modifier'),
    path('supprimer/<int:pk>/',     views.supprimer,      name='supprimer'),
    path('contacter/<int:pk>/',     views.contacter,      name='contacter'),
    path('favoris/toggle/<int:pk>/', views.toggle_favori, name='toggle_favori'),
    path('dashboard/annonces/',          views.dashboard_annonces, name='dashboard_annonces'),
    path('admin-annonces/',         views.admin_annonces, name='admin_annonces'),
    path('admin-annonces/<int:pk>/valider/', views.admin_valider,  name='admin_valider'),   # ← ajouter
    path('admin-annonces/<int:pk>/rejeter/', views.admin_rejeter,  name='admin_rejeter'), 
    path('supprimer-annonce/<int:pk>/', views.supprimer_annonce, name='supprimer_annonce'),
]
