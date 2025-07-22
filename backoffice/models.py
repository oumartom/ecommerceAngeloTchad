from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class AgentProfile(models.Model):
    ROLE_CHOICES = [
        ('agent', 'Agent'),
        ('supervisor', 'Superviseur'),
        ('manager', 'Manager'),
        ('admin', 'Administrateur'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='agent',
        verbose_name="Rôle"
    )
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        verbose_name="Numéro de téléphone"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil Agent"
        verbose_name_plural = "Profils Agents"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin' or self.user.is_superuser
    
    @property
    def can_manage_agents(self):
        """Vérifie si l'utilisateur peut gérer les agents"""
        return self.role in ['admin', 'manager'] or self.user.is_superuser

# Supprimer les signaux automatiques pour éviter les conflits
# @receiver(post_save, sender=User)
# def create_agent_profile(sender, instance, created, **kwargs):
#     """Créer automatiquement un profil agent pour chaque nouvel utilisateur"""
#     if created:
#         AgentProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_agent_profile(sender, instance, **kwargs):
#     """Sauvegarder le profil agent quand l'utilisateur est sauvegardé"""
#     if hasattr(instance, 'agentprofile'):
#         instance.agentprofile.save()

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('order_created', 'Commande créée'),
        ('order_confirmed', 'Commande confirmée'),
        ('order_delivered', 'Commande livrée'),
        ('order_cancelled', 'Commande annulée'),
        ('stock_updated', 'Stock mis à jour'),
        ('product_added', 'Produit ajouté'),
        ('product_updated', 'Produit modifié'),
        ('receipt_generated', 'Reçu généré'),
        ('agent_created', 'Agent créé'),
        ('agent_updated', 'Agent modifié'),
    ]
    
    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Agent"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    description = models.TextField(verbose_name="Description")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Références optionnelles aux objets concernés
    order_id = models.PositiveIntegerField(null=True, blank=True)
    product_id = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activités"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.agent.username} - {self.get_action_display()}"

class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Clé")
    value = models.TextField(verbose_name="Valeur")
    description = models.TextField(blank=True, verbose_name="Description")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Paramètre système"
        verbose_name_plural = "Paramètres système"
    
    def __str__(self):
        return self.key

