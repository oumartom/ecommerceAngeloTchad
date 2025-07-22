#!/usr/bin/env python3
"""
Script de configuration automatique pour Angelo Tchad Orders
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_database():
    """Configure la base de données et crée les données de test"""
    print("🔧 Configuration de la base de données...")
    
    # Appliquer les migrations
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Configurer Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'angelo_tchad_orders.settings')
    django.setup()
    
    from products.models import Product, Category
    from django.contrib.auth.models import User
    from backoffice.models import AgentProfile
    
    print("📦 Création des catégories...")
    categories = [
        Category.objects.get_or_create(name="Électronique", description="Appareils électroniques")[0],
        Category.objects.get_or_create(name="Vêtements", description="Vêtements et accessoires")[0],
        Category.objects.get_or_create(name="Maison", description="Articles pour la maison")[0],
    ]
    
    print("🛍️ Création des produits...")
    products_data = [
        {"name": "Smartphone Samsung", "description": "Smartphone Android dernière génération", "price": 250000, "stock_quantity": 15, "category": categories[0]},
        {"name": "Casque Audio", "description": "Casque audio sans fil Bluetooth", "price": 35000, "stock_quantity": 8, "category": categories[0]},
        {"name": "T-shirt Coton", "description": "T-shirt en coton 100% qualité premium", "price": 5000, "stock_quantity": 50, "category": categories[1]},
        {"name": "Jean Homme", "description": "Jean homme coupe droite", "price": 15000, "stock_quantity": 25, "category": categories[1]},
        {"name": "Lampe LED", "description": "Lampe LED économique", "price": 8000, "stock_quantity": 3, "category": categories[2]},
        {"name": "Chaussures Sport", "description": "Chaussures de sport confortables", "price": 45000, "stock_quantity": 12, "category": categories[1]},
    ]
    
    for product_data in products_data:
        Product.objects.get_or_create(
            name=product_data["name"],
            defaults=product_data
        )
    
    print("👤 Configuration du compte admin...")
    # Créer un superutilisateur par défaut si il n'existe pas
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@angelotchad.com', 'admin123')
        print("   ✅ Compte admin créé (admin/admin123)")
    
    # Créer le profil agent
    admin_user = User.objects.get(username='admin')
    AgentProfile.objects.get_or_create(
        user=admin_user,
        defaults={'role': 'manager', 'is_active': True}
    )
    
    print("✅ Configuration terminée avec succès!")
    print("\n🚀 Pour démarrer le serveur:")
    print("   python manage.py runserver 0.0.0.0:8000")
    print("\n🌐 URLs importantes:")
    print("   Interface client: http://localhost:8000/")
    print("   Back office: http://localhost:8000/backoffice/login/")
    print("   Admin Django: http://localhost:8000/admin/")
    print("\n🔑 Identifiants admin:")
    print("   Utilisateur: admin")
    print("   Mot de passe: admin123")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_database()
    else:
        print("Usage: python setup.py setup")

