from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from  django.core.paginator import Paginator


from .models import Annonce, Bien, Localisation, Image, Favori, Contact, TRANSACTION_CHOICES, TYPE_BIEN_CHOICES
from .forms import InscriptionForm, BienForm, LocalisationForm, ContactForm, RechercheForm


def home(request):
    annonces = Annonce.objects.filter(statut='validee').select_related('bien__localisation')

    q           = request.GET.get('q', '').strip()
    transaction = request.GET.get('transaction', '')
    type_bien   = request.GET.get('type_bien', '')
    ville       = request.GET.get('ville', '').strip()
    prix_min    = request.GET.get('prix_min', '')
    prix_max    = request.GET.get('prix_max', '')

    if q:
        annonces = annonces.filter(
            Q(bien__titre__icontains=q) |
            Q(bien__description__icontains=q) |
            Q(bien__quartier__icontains=q) |
            Q(bien__localisation__ville__icontains=q)
        )
    if transaction:
        annonces = annonces.filter(bien__categorie=transaction)
    if type_bien:
        annonces = annonces.filter(bien__type_bien=type_bien)
    if ville:
        annonces = annonces.filter(bien__localisation__ville__icontains=ville)
    if prix_min:
        try: annonces = annonces.filter(bien__prix__gte=float(prix_min))
        except ValueError: pass
    if prix_max:
        try: annonces = annonces.filter(bien__prix__lte=float(prix_max))
        except ValueError: pass

    # IDs favoris de l'utilisateur connecté
    favoris_ids = []
    if request.user.is_authenticated:
        favoris_ids = list(Favori.objects.filter(
          
            utilisateur=request.user
        ).values_list('annonce_id', flat=True))
    paginator = Paginator(annonces, 3)
    page_number = request.GET.get('page', 1)
    annonces = paginator.get_page(page_number)
    context = {
        'annonces':          annonces,
        'type_bien_choices': TYPE_BIEN_CHOICES,
        'favoris_ids':       favoris_ids,
    }
    
    paginator = Paginator(annonces, 3)  
    page_number = request.GET.get('page', 1)
    annonces = paginator.get_page(page_number)
    return render(request, 'immobilier/home.html', context)



def detail_annonce(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, statut='validee')
    # Incrémenter le compteur de vues
    annonce.vues += 1
    annonce.save(update_fields=['vues'])

    est_favori = False
    if request.user.is_authenticated:
        est_favori = Favori.objects.filter(utilisateur=request.user, annonce=annonce).exists()

    return render(request, 'immobilier/detail.html', {
        'annonce':    annonce,
        'est_favori': est_favori,
        'form_contact': ContactForm(),
    })

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
            return redirect('home')
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()
    return render(request, 'immobilier/inscription.html', {'form': form})



def connexion(request):
    if request.user.is_authenticated:
        return redirect('tableauBord')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'tableauBord'))
        error = "Identifiants incorrects."
    return render(request, 'immobilier/connexion.html', {'error': error})

def deconnexion(request):
    logout(request)
    return redirect('home')

@login_required
def tableauBord(request):
    mes_biens    = Bien.objects.filter(proprietaire=request.user).prefetch_related('images', 'annonce')
    mes_favoris  = Favori.objects.filter(utilisateur=request.user).select_related('annonce__bien')
    mes_messages = Contact.objects.filter(annonce__bien__proprietaire=request.user)
    non_lus      = mes_messages.filter(lu=False).count()

    # Stats pour les cards a droite
    total_biens     = mes_biens.count()
    biens_vente     = mes_biens.filter(categorie='vente').count()
    biens_location  = mes_biens.filter(categorie='location').count()
    total_favoris   = mes_favoris.count()

    return render(request, 'immobilier/tableauBord.html', {
        'mes_biens':     mes_biens,
        'mes_favoris':   mes_favoris,
        'non_lus':       non_lus,
        'total_biens':   total_biens,
        'biens_vente':   biens_vente,
        'biens_location': biens_location,
        'total_favoris': total_favoris,
    })

@login_required
def ajouter(request):
    if request.method == 'POST':
        form_bien  = BienForm(request.POST)
        form_loc   = LocalisationForm(request.POST)

        if form_bien.is_valid() and form_loc.is_valid():
            # 1. Sauvegarder localisation
            localisation = form_loc.save()

            # 2. Sauvegarder le bien
            bien = form_bien.save(commit=False)
            bien.proprietaire = request.user
            bien.localisation = localisation
            bien.save()

            # 3. Créer l'annonce (statut = en_attente par défaut)
            Annonce.objects.create(bien=bien)

            # 4. Sauvegarder les images
            images = request.FILES.getlist('photos')
            for i, img in enumerate(images[:10]):
                Image.objects.create(bien=bien, fichier=img, imagePrincipale=(i == 0))

            messages.success(request, "Votre annonce a été soumise et est en attente de validation.")
            return redirect('tableauBord')
        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form_bien = BienForm()
        form_loc  = LocalisationForm()

    return render(request, 'immobilier/ajouter.html', {
        'form_bien': form_bien,
        'form_loc':  form_loc,
    })

def logement(request):
    annonces = Annonce.objects.filter(statut='validee').select_related('bien__localisation')
    paginator = Paginator(annonces, 3)
    page_number = request.GET.get('page', 1)
    annonces = paginator.get_page(page_number)
    return render(request, 'immobilier/logement.html', {
        'annonces': annonces,
        'type_bien_choices': TYPE_BIEN_CHOICES,
        
    })

@login_required
def modifier(request, pk):
    bien   = get_object_or_404(Bien, pk=pk, proprietaire=request.user)
    annonce = bien.annonce

    if request.method == 'POST':
        form_bien = BienForm(request.POST, instance=bien)
        form_loc  = LocalisationForm(request.POST, instance=bien.localisation)
        if form_bien.is_valid() and form_loc.is_valid():
            form_loc.save()
            form_bien.save()
            annonce.statut = 'en_attente'  
            annonce.save()
            # Nouvelles images si fournies
            for i, img in enumerate(request.FILES.getlist('photos')):
                Image.objects.create(bien=bien, fichier=img)
            messages.success(request, "Annonce modifiée. En attente de re-validation.")
            return redirect('tableauBord')
    else:
        form_bien = BienForm(instance=bien, initial={'categorie': bien.categorie})
        form_loc  = LocalisationForm(instance=bien.localisation)

    return render(request, 'immobilier/modifier.html', {
        'form_bien': form_bien,
        'form_loc':  form_loc,
        'bien':      bien,
    })


@login_required
def supprimer(request, pk):
    bien = get_object_or_404(Bien, pk=pk, proprietaire=request.user)

    # Récupère l'URL de retour (admin ou tableau de bord)
    retour = request.GET.get('retour', 'tableauBord')

    if request.method == 'POST':
        bien.delete()
        messages.success(request, "Annonce supprimée avec succès.")
        # Redirige vers la bonne page selon qui a supprimé
        retour_post = request.POST.get('retour', 'tableauBord')
        return redirect(retour_post)

    return render(request, 'immobilier/supprimer.html', {
    'bien':   bien,
    'retour': retour,  # ← on passe l'URL de retour au template
})


@login_required
def contacter(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, statut='validee')
    if annonce.bien.proprietaire == request.user:
        messages.warning(request, "Vous ne pouvez pas vous contacter vous-même.")
        return redirect('detail_annonce', pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.annonce    = annonce
            c.expediteur = request.user
            c.save()
            messages.success(request, "Message envoyé au propriétaire !")
    return redirect('detail_annonce', pk=pk)



@login_required
def toggle_favori(request, pk):
    if request.method == 'POST':
        annonce = get_object_or_404(Annonce, pk=pk)
        favori, created = Favori.objects.get_or_create(
            utilisateur=request.user, annonce=annonce
        )
        if not created:
            favori.delete()
            return JsonResponse({'active': False})
        return JsonResponse({'active': True})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



@login_required
def favoris(request):
    """Page listant tous les favoris de l'utilisateur"""
    mes_favoris = Favori.objects.filter(utilisateur=request.user).select_related('annonce__bien')
    return render(request, 'immobilier/favoris.html', {'mes_favoris': mes_favoris})


@login_required
def mes_messages(request):
    contacts = Contact.objects.filter(
        annonce__bien__proprietaire=request.user
    ).select_related('expediteur', 'annonce__bien')
    contacts.update(lu=True)
    return render(request, 'immobilier/messages.html', {'contacts': contacts})

@login_required
def dashboard_annonces(request):
    """API pour DataTables - liste des annonces de l'utilisateur"""
    annonces = Annonce.objects.filter(bien__proprietaire=request.user).select_related('bien__localisation')
    data = []
    for a in annonces:
        data.append({
            'id': a.id,
            'titre': a.bien.titre,
            'categorie': a.bien.get_categorie_display(),
            'type_bien': a.bien.get_type_bien_display(),
            'prix': f"{a.bien.prix:,.2f} €",
            'ville': a.bien.localisation.ville,
            'statut': a.get_statut_display(),
            'vues': a.vues,
        })
    return render(request, 'immobilier/dashboardAdmin.html', {'data': data})

@login_required
def admin_annonces(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    statut = request.GET.get('statut', '')
    annonces = Annonce.objects.all().select_related('bien__localisation', 'bien__proprietaire')

    if statut:
        annonces = annonces.filter(statut=statut)

    return render(request, 'immobilier/admin_annonces.html', {
    'annonces':         annonces,
    'total_count':      Annonce.objects.count(),
    'en_attente_count': Annonce.objects.filter(statut='en_attente').count(),
    'validee_count':    Annonce.objects.filter(statut='validee').count(),
    'rejetee_count':    Annonce.objects.filter(statut='rejetee').count(),
})
    
@login_required
def admin_valider(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == 'POST':
        annonce = get_object_or_404(Annonce, pk=pk)
        annonce.statut = 'validee'
        annonce.save()
        messages.success(request, f"Annonce « {annonce.bien.titre} » validée.")
        return redirect('admin_annonces')


@login_required
def admin_rejeter(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == 'POST':
        annonce = get_object_or_404(Annonce, pk=pk)
        annonce.statut = 'rejetee'
        annonce.save()
        messages.warning(request, f"Annonce « {annonce.bien.titre} » rejetée.")
        return redirect('admin_annonces')

@login_required
def supprimer_annonce(request, pk):
    # 1. On récupère le bien par son ID
    bien = get_object_or_404(Bien, pk=pk)

    # 2. Vérification des droits : admin OU propriétaire
    if bien.proprietaire != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette annonce.")
        return redirect('tableauBord')

    # 3. Traitement de la suppression
    if request.method == 'POST':
        bien.delete()
        messages.success(request, "Annonce supprimée avec succès.")
        # Redirection dynamique
        retour = request.POST.get('retour', 'tableauBord')
        return redirect(retour)

    # 4. GET → affiche la page de confirmation avec le paramètre retour
    retour = request.GET.get('retour', 'tableauBord')
    return render(request, 'immobilier/supprimer.html', {
    'bien': bien,
    'retour': retour  # Important : passer retour au template
})