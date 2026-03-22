"""
models.py - Modèles Django basés sur le diagramme de classes
Classes : Utilisateur (via Django User), Localisation, Bien, Annonce, Image, Favori, Contact
"""
from django.db import models
from django.contrib.auth.models import User


# Choix globaux (utilisés dans plusieurs modèles)
TRANSACTION_CHOICES = [
    ('vente',    'Vente'),
    ('location', 'Location'),
]

TYPE_BIEN_CHOICES = [
    ('appartement', 'Appartement'),
    ('maison',      'Maison'),
    ('terrain',     'Terrain'),
    ('local',       'Local commercial'),
    ('bureau',      'Bureau'),
    ('garage',      'Garage / Parking'),
]


class Localisation(models.Model):
    """Coordonnées géographiques d'un bien (pour la carte Leaflet)"""
    ville     = models.CharField(max_length=100, default='')
    quartier  = models.CharField(max_length=100, blank=True, default='')
    adresse   = models.CharField(max_length=255, blank=True, default='')
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.ville} – {self.quartier}"

    class Meta:
        verbose_name = "Localisation"


class Bien(models.Model):
    """
    Un bien immobilier.
    Lié à : Localisation (1-1), User/proprietaire (N-1), Annonce (1-1), Images (1-N)
    """
    titre       = models.CharField(max_length=200)
    description = models.TextField()
    categorie   = models.CharField(max_length=20, choices=TRANSACTION_CHOICES, default='vente',
                                   verbose_name="Type de transaction")
    type_bien   = models.CharField(max_length=50, choices=TYPE_BIEN_CHOICES, default='appartement')
    prix        = models.FloatField(help_text="Prix en FCFA")
    surface     = models.FloatField(help_text="Surface en m²")
    nb_pieces   = models.IntegerField(default=1, verbose_name="Nombre de pièces")
    quartier    = models.CharField(max_length=100, blank=True)

    # Relation avec Localisation
    localisation = models.OneToOneField(Localisation, on_delete=models.CASCADE,
                                        null=True, blank=True, related_name='bien')
    # Propriétaire du bien (utilise le User Django)
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='biens', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    def get_image_principale(self):
        """Retourne l'image principale ou la première image"""
        img = self.images.filter(imagePrincipale=True).first()
        return img or self.images.first()

    class Meta:
        verbose_name = "Bien"
        ordering = ['-created_at']


class Image(models.Model):
    """Images d'un bien - relation 1-N (un bien a plusieurs images)"""
    bien           = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='images')
    fichier        = models.ImageField(upload_to='biens/', blank=True, null=True)
    imagePrincipale = models.BooleanField(default=False)

    def __str__(self):
        return f"Image de {self.bien.titre}"

    class Meta:
        verbose_name = "Image"


class Annonce(models.Model):
    """
    Annonce publiée pour un bien.
    Statut géré par l'admin : en_attente → validee ou rejetee
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee',    'Validée'),
        ('rejetee',    'Rejetée'),
    ]
    bien            = models.OneToOneField(Bien, on_delete=models.CASCADE, related_name='annonce')
    statut          = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    vues            = models.IntegerField(default=0)
    datePublication = models.DateTimeField(auto_now_add=True)
    dateExpiration  = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.bien.titre} [{self.get_statut_display()}]"

    class Meta:
        verbose_name = "Annonce"
        ordering = ['-datePublication']


class Contact(models.Model):
    """Message envoyé au propriétaire via une annonce"""
    annonce    = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='contacts')
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    message    = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu         = models.BooleanField(default=False)

    def __str__(self):
        return f"Message de {self.expediteur.username} → {self.annonce}"

    class Meta:
        verbose_name = "Contact"
        ordering = ['-date_envoi']


class Favori(models.Model):
    """Favoris d'un utilisateur - relation N-N entre User et Annonce"""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris')
    annonce     = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='favoris')
    dateAjout   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilisateur', 'annonce')  # Pas de doublon
        verbose_name = "Favori"

    def __str__(self):
        return f"{self.utilisateur.username} ♥ {self.annonce.bien.titre}"
