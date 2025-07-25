from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from products.models import Product
import uuid

class Client(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    
    # Validation du numéro de téléphone tchadien
    phone_regex = RegexValidator(
        regex=r'^\+235\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}$',
        message="Le numéro doit être au format: +235 XX XX XX XX"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Numéro de téléphone"
    )
    
    neighborhood = models.CharField(max_length=200, verbose_name="Quartier")
    address_details = models.TextField(blank=True, verbose_name="Détails de l'adresse")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro de commande"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name="Client"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant total"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de confirmation")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de livraison")
    
    # Agent qui gère la commande
    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Agent assigné"
    )
    
    # Gestion du stock
    stock_deducted = models.BooleanField(default=False, verbose_name="Stock déduit")
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Générer un numéro de commande si nouveau
        if not self.order_number:
            self.order_number = f"AT{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Gestion automatique du stock
        if self.pk:  # Si la commande existe déjà
            try:
                old_order = Order.objects.get(pk=self.pk)
                
                # Si le statut passe à 'confirmed' et le stock n'a pas encore été déduit
                if (old_order.status != 'confirmed' and self.status == 'confirmed' 
                    and not self.stock_deducted):
                    self.deduct_stock()
                    self.confirmed_at = timezone.now()
                
                # Si le statut passe à 'cancelled' et le stock a été déduit, restaurer le stock
                elif (old_order.status != 'cancelled' and self.status == 'cancelled' 
                      and self.stock_deducted):
                    self.restore_stock()
                    
            except Order.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def deduct_stock(self):
        for item in self.items.all():
            product = item.product
            product.stock_quantity -= item.quantity
            try:
                product.save()
            except Exception as e:
                print(f"Erreur lors du save de {product}: {e}")
                raise
    # def deduct_stock(self):
    #     """Déduit le stock des produits de la commande"""
    #     for item in self.items.all():
    #         product = item.product
    #         if product.stock_quantity >= item.quantity:
    #             product.stock_quantity -= item.quantity
    #             product.save()
    #             print(f"Stock déduit pour {product.name}: -{item.quantity} (nouveau stock: {product.stock_quantity})")
    #         else:
    #             raise ValidationError(
    #                 f"Stock insuffisant pour {product.name}. "
    #                 f"Stock disponible: {product.stock_quantity}, "
    #                 f"Quantité demandée: {item.quantity}"
    #             )
        
    #     self.stock_deducted = True
        
    #     # Log de l'activité
    #     try:
    #         from backoffice.models import ActivityLog
    #         ActivityLog.objects.create(
    #             action='stock_deducted',
    #             description=f'Stock déduit automatiquement pour la commande {self.order_number}',
    #             order_id=self.id
    #         )
    #     except:
    #         pass  # En cas d'erreur, ne pas bloquer la sauvegarde
    
    def restore_stock(self):
        """Restaure le stock des produits en cas d'annulation"""
        for item in self.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
            print(f"Stock restauré pour {product.name}: +{item.quantity} (nouveau stock: {product.stock_quantity})")
        
        self.stock_deducted = False
        
        # Log de l'activité
        try:
            from backoffice.models import ActivityLog
            ActivityLog.objects.create(
                action='stock_restored',
                description=f'Stock restauré automatiquement pour la commande annulée {self.order_number}',
                order_id=self.id
            )
        except:
            pass  # En cas d'erreur, ne pas bloquer la sauvegarde
    
    def can_be_confirmed(self):
        """Vérifie si la commande peut être confirmée (stock suffisant)"""
        for item in self.items.all():
            if item.product.stock_quantity < item.quantity:
                return False, f"Stock insuffisant pour {item.product.name}"
        return True, "OK"
    
    def calculate_total(self):
        """Calcule le montant total de la commande"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
    
    def __str__(self):
        return f"Commande {self.order_number} - {self.client.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Commande"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Produit"
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix unitaire"
    )
    
    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
        unique_together = ['order', 'product']
    
    def save(self, *args, **kwargs):
        # Sauvegarder le prix au moment de la commande
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
    
    @property
    def subtotal(self):
        if self.quantity is None or self.unit_price is None:
            return 0
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

