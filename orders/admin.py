from django.contrib import admin
from .models import Client, Order, OrderItem

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'neighborhood', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone_number', 'neighborhood']
    list_filter = ['neighborhood', 'created_at']
    ordering = ['last_name', 'first_name']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    
    def subtotal(self, obj):
        return f"{obj.subtotal} FCFA" if obj.subtotal else "0 FCFA"
    subtotal.short_description = "Sous-total"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'client', 'status', 'total_amount', 'created_at', 'assigned_agent']
    list_filter = ['status', 'created_at', 'assigned_agent']
    search_fields = ['order_number', 'client__first_name', 'client__last_name', 'client__phone_number']
    list_editable = ['status', 'assigned_agent']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations de commande', {
            'fields': ('order_number', 'client', 'status', 'assigned_agent')
        }),
        ('Montants', {
            'fields': ('total_amount',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalculer le total après sauvegarde
        obj.calculate_total()

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status', 'product__category']
    search_fields = ['order__order_number', 'product__name']

