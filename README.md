# Système de Gestion de Commandes Angelo Tchad

## 🎯 Vue d'ensemble

Le système de gestion de commandes Angelo Tchad est une solution complète de e-commerce développée avec Django et Bootstrap, spécialement conçue pour les entreprises tchadiennes. Il comprend une interface client moderne et un back office professionnel pour la gestion des commandes.

## ✨ Fonctionnalités principales

### Interface Client
- **Catalogue de produits** avec catégories (Maison, Vêtements, Électronique)
- **Panier d'achat** interactif avec gestion des quantités
- **Processus de commande** simplifié avec validation des données
- **Suivi de commande** en temps réel
- **Format téléphone tchadien** (+235 XX XX XX XX)
- **Quartiers de N'Djaména** pour la livraison

### Back Office pour Agents
- **Dashboard complet** avec statistiques en temps réel
- **Gestion des commandes** avec filtres et recherche
- **Gestion du stock** avec alertes de stock faible
- **Génération automatique de reçus PDF** pour la livraison
- **Suivi des clients** et historique des commandes
- **Journal d'activité** pour traçabilité complète

### Gestion Automatique du Stock
- **Déduction automatique** lors de la confirmation de commande
- **Restauration du stock** en cas d'annulation
- **Alertes de stock faible** dans le dashboard
- **Vérification de disponibilité** avant confirmation

### Système de Reçus
- **Génération PDF automatique** pour chaque commande confirmée
- **Informations complètes** : client, produits, montants, dates
- **Design professionnel** avec logo Angelo Tchad
- **Téléchargement direct** depuis le back office

## 🏗️ Architecture Technique

### Backend
- **Django 4.x** - Framework web Python
- **SQLite** - Base de données intégrée
- **Django REST Framework** - API REST
- **ReportLab** - Génération de PDF

### Frontend
- **Bootstrap 5** - Framework CSS responsive
- **JavaScript vanilla** - Interactions dynamiques
- **Font Awesome** - Icônes professionnelles
- **Design responsive** - Compatible mobile et desktop

### Modèles de Données
- **Client** : Prénom, nom, téléphone, quartier, adresse
- **Produit** : Nom, description, prix, stock, catégorie, image
- **Commande** : Numéro unique, statut, montant, dates, agent assigné
- **OrderItem** : Articles de commande avec quantités
- **AgentProfile** : Profils des agents du back office
- **ActivityLog** : Journal des activités pour traçabilité

## 🚀 Installation et Configuration

### Prérequis
```bash
- Python 3.8+
- pip (gestionnaire de paquets Python)
- Git (optionnel)
```

### Installation
```bash
# 1. Naviguer vers le dossier du projet
cd angelo_tchad_orders

# 2. Installer les dépendances
pip install django djangorestframework django-cors-headers reportlab pillow

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer un superutilisateur
python manage.py createsuperuser

# 5. Créer des données de test
python manage.py shell
# Exécuter le script de données de test (voir section suivante)

# 6. Lancer le serveur
python manage.py runserver 0.0.0.0:8000
```

### Données de Test
```python
# Script à exécuter dans le shell Django
from products.models import Product, Category
from django.contrib.auth.models import User
from backoffice.models import AgentProfile

# Créer les catégories
categories = [
    Category.objects.get_or_create(name="Électronique", description="Appareils électroniques")[0],
    Category.objects.get_or_create(name="Vêtements", description="Vêtements et accessoires")[0],
    Category.objects.get_or_create(name="Maison", description="Articles pour la maison")[0],
]

# Créer des produits
products_data = [
    {"name": "Smartphone Samsung", "description": "Smartphone Android dernière génération", "price": 250000, "stock": 15, "category": categories[0]},
    {"name": "Casque Audio", "description": "Casque audio sans fil Bluetooth", "price": 35000, "stock": 8, "category": categories[0]},
    {"name": "T-shirt Coton", "description": "T-shirt en coton 100% qualité premium", "price": 5000, "stock": 50, "category": categories[1]},
    {"name": "Jean Homme", "description": "Jean homme coupe droite", "price": 15000, "stock": 25, "category": categories[1]},
    {"name": "Lampe LED", "description": "Lampe LED économique", "price": 8000, "stock": 3, "category": categories[2]},
    {"name": "Chaussures Sport", "description": "Chaussures de sport confortables", "price": 45000, "stock": 12, "category": categories[1]},
]

for product_data in products_data:
    Product.objects.get_or_create(**product_data)

# Créer un profil agent pour l'admin
admin_user = User.objects.get(username='admin')
AgentProfile.objects.get_or_create(
    user=admin_user,
    defaults={'role': 'manager', 'is_active': True}
)

print("Données de test créées avec succès!")
```

## 📱 Utilisation

### Interface Client
1. **Accueil** : `http://localhost:8000/`
   - Parcourir les produits par catégorie
   - Ajouter des articles au panier
   - Voir les détails des produits

2. **Panier** : `http://localhost:8000/cart/`
   - Modifier les quantités
   - Supprimer des articles
   - Voir le total de la commande

3. **Commande** : `http://localhost:8000/checkout/`
   - Saisir les informations client
   - Choisir le mode de paiement
   - Confirmer la commande

4. **Suivi** : `http://localhost:8000/track/`
   - Suivre l'état de sa commande
   - Voir l'historique

### Back Office Agents
1. **Connexion** : `http://localhost:8000/backoffice/login/`
   - Utiliser les identifiants admin créés

2. **Dashboard** : `http://localhost:8000/backoffice/`
   - Vue d'ensemble des statistiques
   - Commandes récentes
   - Alertes de stock

3. **Gestion des Commandes** : `http://localhost:8000/backoffice/orders/`
   - Liste complète des commandes
   - Filtres par statut
   - Recherche par client/numéro

4. **Détail Commande** : `http://localhost:8000/backoffice/orders/{id}/`
   - Informations complètes
   - Changement de statut
   - Génération de reçu

5. **Gestion Stock** : `http://localhost:8000/backoffice/products/`
   - Liste des produits
   - Mise à jour du stock
   - Alertes de rupture

## 📊 Statuts des Commandes

1. **En attente** (pending) - Commande créée, en attente de traitement
2. **Confirmée** (confirmed) - Commande validée, stock déduit
3. **En préparation** (preparing) - Articles en cours de préparation
4. **Prête** (ready) - Commande prête pour livraison
5. **En livraison** (delivering) - En cours de livraison
6. **Livrée** (delivered) - Commande livrée avec succès
7. **Annulée** (cancelled) - Commande annulée, stock restauré

## 🎨 Personnalisation

### Couleurs et Thème
- **Couleur principale** : Vert Angelo Tchad (#28a745)
- **Couleurs secondaires** : Bleu, orange, rouge pour les statuts
- **Responsive design** : Compatible tous écrans

### Logo et Branding
- Remplacer le logo dans `/static/images/logo.png`
- Modifier les couleurs dans `/static/css/style.css`
- Personnaliser les templates dans `/templates/`

## 🔧 Configuration Avancée

### Variables d'Environnement
```python
# settings.py
DEBUG = False  # En production
ALLOWED_HOSTS = ['votre-domaine.com']
STATIC_ROOT = '/path/to/static/'
MEDIA_ROOT = '/path/to/media/'
```

### Base de Données Production
```python
# Pour PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'angelo_tchad_db',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📞 Support et Contact

- **Téléphone** : +235 XX XX XX XX
- **Email** : contact@angelotchad.com
- **Adresse** : N'Djaména, Tchad

## 🔒 Sécurité

- **Authentification** requise pour le back office
- **Validation** des données côté serveur
- **Protection CSRF** activée
- **Logs d'activité** pour traçabilité

## 📈 Statistiques Disponibles

- Total des commandes
- Commandes en attente
- Commandes confirmées
- Commandes livrées
- Montant total des ventes
- Évolution sur 7 jours
- Produits en stock faible
- Activité des agents

## 🚀 Déploiement

Le système est prêt pour le déploiement sur :
- **Serveurs VPS** (Ubuntu, CentOS)
- **Plateformes cloud** (AWS, DigitalOcean, Heroku)
- **Serveurs locaux** pour usage interne

---

**Développé avec ❤️ pour Angelo Tchad**
*Votre partenaire pour les commandes en ligne au Tchad*

