from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Client, Order, OrderItem
from products.models import Product, Category
from .forms import ClientForm, OrderForm
import json

def home(request):
    """Page d'accueil avec liste des produits"""
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    
    # Filtrer par catégorie si spécifiée
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'categories': categories,
        'products': products,
        'selected_category': int(category_id) if category_id else None
    }
    return render(request, 'orders/home.html', context)

def product_detail(request, product_id):
    """Détail d'un produit"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'orders/product_detail.html', {'product': product})

def cart_view(request):
    """Affichage du panier"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            # Supprimer le produit du panier s'il n'existe plus
            del cart[product_id]
            request.session['cart'] = cart
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': sum(cart.values())
    }
    return render(request, 'orders/cart.html', context)


from django.shortcuts import redirect


def add_to_cart(request):
    """Ajouter un produit au panier (AJAX ou formulaire classique)"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, is_active=True)
            cart = request.session.get('cart', {})
            current_quantity = cart.get(str(product_id), 0)

            if current_quantity + quantity > product.stock_quantity:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Stock insuffisant.'})
                else:
                    # Tu peux rediriger vers produit avec un message si tu veux
                    return redirect('orders:cart')

            # Ajouter au panier
            cart[str(product_id)] = current_quantity + quantity
            request.session['cart'] = cart

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} ajouté au panier',
                    'cart_count': sum(cart.values())
                })
            else:
                return redirect('orders:cart')

        except Product.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Produit introuvable'})
            else:
                return redirect('orders:cart')

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})


def update_cart(request):
    """Mettre à jour la quantité dans le panier (AJAX)"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        
        cart = request.session.get('cart', {})
        
        if quantity <= 0:
            # Supprimer du panier
            if str(product_id) in cart:
                del cart[str(product_id)]
        else:
            # Vérifier le stock
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                if quantity > product.stock_quantity:
                    return JsonResponse({
                        'success': False,
                        'message': f'Stock insuffisant. Disponible: {product.stock_quantity}'
                    })
                cart[str(product_id)] = quantity
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Produit non trouvé'
                })
        
        request.session['cart'] = cart
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values())
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

def checkout(request):
    """Page de commande"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('orders:home')
    
    # Calculer le total et préparer les items
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Vérifier le stock avant la commande
            if quantity > product.stock_quantity:
                messages.error(request, f'Stock insuffisant pour {product.name}. Disponible: {product.stock_quantity}')
                return redirect('orders:cart')
            
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            messages.error(request, 'Un produit de votre panier n\'est plus disponible.')
            return redirect('orders:cart')
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        print("Numéro soumis:", request.POST.get('phone_number'))  # Debug
        if form.is_valid():
            print("Numéro validé:", form.cleaned_data['phone_number'])  # Debug
            # ... reste du code ...
            try:
                with transaction.atomic():
                    # Créer ou récupérer le client
                    client_data = form.cleaned_data
                    client, created = Client.objects.get_or_create(
                        phone_number=client_data['phone_number'],
                        defaults=client_data
                    )
                    
                    # Créer la commande
                    order = Order.objects.create(
                        client=client,
                        total_amount=total
                    )
                    
                    # Créer les items de commande
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            quantity=item['quantity'],
                            unit_price=item['product'].price
                        )
                    
                    # Vider le panier
                    request.session['cart'] = {}
                    
                    messages.success(request, f'Votre commande {order.order_number} a été créée avec succès!')
                    return redirect('orders:order_success', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, 'Une erreur est survenue lors de la création de votre commande.')
                return redirect('orders:checkout')
    else:
        form = ClientForm()
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'orders/checkout.html', context)

def order_success(request, order_id):
    """Page de confirmation de commande"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})

# def order_tracking(request):
#     """Suivi de commande"""
#     order = None
#     error_message = None
    
#     if request.method == 'POST':
#         order_number = request.POST.get('order_number', '').strip()
#         phone_number = request.POST.get('phone_number', '').strip()
        
#         if not order_number or not phone_number:
#             error_message = 'Veuillez saisir le numéro de commande et le numéro de téléphone.'
#         else:
#             try:
#                 # Recherche avec différentes variantes du numéro de téléphone
#                 order = Order.objects.select_related('client').get(
#                     order_number__iexact=order_number,
#                     client__phone_number__icontains=phone_number.replace(' ', '').replace('+235', '').replace('+', '')
#                 )
#             except Order.DoesNotExist:
#                 # Essayer une recherche plus flexible
#                 try:
#                     # Nettoyer le numéro de téléphone pour la recherche
#                     clean_phone = phone_number.replace(' ', '').replace('-', '').replace('+235', '').replace('+', '')
                    
#                     order = Order.objects.select_related('client').filter(
#                         order_number__iexact=order_number
#                     ).filter(
#                         client__phone_number__icontains=clean_phone
#                     ).first()
                    
#                     if not order:
#                         error_message = 'Commande non trouvée. Vérifiez le numéro de commande et le numéro de téléphone.'
#                 except Exception as e:
#                     error_message = 'Erreur lors de la recherche. Veuillez réessayer.'
    
#     context = {
#         'order': order,
#         'error_message': error_message
#     }
#     return render(request, 'orders/order_tracking.html', context)

import logging

logger = logging.getLogger(__name__)

def order_tracking(request):
    order = None
    error_message = None

    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        logger.info(f"Recherche commande : numéro {order_number} | téléphone {phone_number}")

        # Nettoyage basique
        phone_clean = phone_number.replace(' ', '').replace('+235', '').replace('+', '')

        try:
            # Récupère toutes les commandes avec ce numéro
            orders = Order.objects.filter(order_number__iexact=order_number)
            logger.info(f"Commandes trouvées : {[o.client.phone_number for o in orders]}")

            for o in orders:
                client_phone = o.client.phone_number.replace(' ', '').replace('+235', '').replace('+', '')
                if phone_clean in client_phone or client_phone in phone_clean:
                    order = o
                    break

            if not order:
                error_message = 'Commande non trouvée. Vérifiez le numéro de commande et le numéro de téléphone.'

        except Exception as e:
            logger.error(f"Erreur lors de la recherche : {e}")
            error_message = 'Erreur lors de la recherche. Veuillez réessayer.'

    context = {
        'order': order,
        'error_message': error_message
    }
    return render(request, 'orders/order_tracking.html', context)


