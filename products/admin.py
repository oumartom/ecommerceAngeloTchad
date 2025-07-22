from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock_quantity', 'is_active']
    ordering = ['name']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'category', 'description', 'image')
        }),
        ('Prix et stock', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )

