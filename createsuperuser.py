import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealEaste.settings')
django.setup()

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superutilisateur créé avec succès !")
else:
    print("Le superutilisateur existe déjà.")
