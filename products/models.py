from django.db import models
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    description = models.TextField(blank=True, verbose_name="Description")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Prix"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité en stock"
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Image du produit"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    def reduce_stock(self, quantity):
        """Réduit le stock du produit"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Ajouter la relation avec Category au modèle Product
Product.add_to_class('category', models.ForeignKey(
    Category, 
    on_delete=models.SET_NULL, 
    null=True, 
    blank=True,
    verbose_name="Catégorie"
))

