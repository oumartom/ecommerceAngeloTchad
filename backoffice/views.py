from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from orders.models import Order, OrderItem, Client
from products.models import Product
from .models import AgentProfile, ActivityLog
from .forms import AgentCreationForm, AgentUpdateForm
import json
import openpyxl
def agent_login(request):
    """Page de connexion pour les agents"""
    if request.user.is_authenticated:
        return redirect('backoffice:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'agentprofile') and user.agentprofile.is_active:
                login(request, user)
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username}!')
                return redirect('backoffice:dashboard')
            else:
                messages.error(request, 'Votre compte n\'est pas autorisé à accéder au back office.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'backoffice/login.html')

@login_required
def agent_logout(request):
    """Déconnexion des agents"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('backoffice:login')

# @login_required
# def dashboard(request):
#     """Dashboard principal avec statistiques"""
#     # Statistiques générales
#     total_orders = Order.objects.count()
#     pending_orders = Order.objects.filter(status='pending').count()
#     confirmed_orders = Order.objects.filter(status='confirmed').count()
#     delivered_orders = Order.objects.filter(status='delivered').count()
    
#     # Montant total
#     total_amount = Order.objects.aggregate(
#         total=Sum('total_amount')
#     )['total'] or 0
    
#     # Commandes récentes
#     recent_orders = Order.objects.select_related('client').order_by('-created_at')[:10]
    
#     # Produits en rupture de stock
#     low_stock_products = Product.objects.filter(
#         stock_quantity__lte=5, 
#         is_active=True
#     ).order_by('stock_quantity')[:5]
    
#     # Statistiques par jour (7 derniers jours)
#     today = timezone.now().date()
#     week_ago = today - timedelta(days=7)
    
#     daily_stats = []
#     for i in range(7):
#         date = week_ago + timedelta(days=i)
#         orders_count = Order.objects.filter(created_at__date=date).count()
#         daily_stats.append({
#             'date': date.strftime('%d/%m'),
#             'orders': orders_count
#         })
    
#     context = {
#         'total_orders': total_orders,
#         'pending_orders': pending_orders,
#         'confirmed_orders': confirmed_orders,
#         'delivered_orders': delivered_orders,
#         'total_amount': total_amount,
#         'recent_orders': recent_orders,
#         'low_stock_products': low_stock_products,
#         'daily_stats': daily_stats,
#     }
    
#     return render(request, 'backoffice/dashboard.html', context)
@login_required
def dashboard(request):
    """Dashboard principal avec statistiques"""
    # Statistiques générales commandes
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Montant total des commandes
    total_amount = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Commandes récentes
    recent_orders = Order.objects.select_related('client').order_by('-created_at')[:10]
    
    # Produits en rupture de stock
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=5, 
        is_active=True
    ).order_by('stock_quantity')[:5]
    
    # Statistiques par jour (7 derniers jours)
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        date = week_ago + timedelta(days=i)
        orders_count = Order.objects.filter(created_at__date=date).count()
        daily_stats.append({
            'date': date.strftime('%d/%m'),
            'orders': orders_count
        })
    
    # === Statistiques des clients ===
    total_clients = Client.objects.count()

    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_clients = Client.objects.filter(created_at__gte=thirty_days_ago).count()

    seven_days_ago = timezone.now() - timedelta(days=7)
    new_clients = Client.objects.filter(created_at__gte=seven_days_ago).count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'delivered_orders': delivered_orders,
        'total_amount': total_amount,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'daily_stats': daily_stats,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'new_clients': new_clients,
    }

    return render(request, 'backoffice/dashboard.html', context)

@login_required
def orders_list(request):
    """Liste des commandes avec filtres"""
    orders = Order.objects.select_related('client', 'assigned_agent').order_by('-created_at')
    
    # Filtres
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(client__first_name__icontains=search) |
            Q(client__last_name__icontains=search) |
            Q(client__phone_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'backoffice/orders_list.html', context)

@login_required
def order_detail(request, order_id):
    """Détail d'une commande"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Order.STATUS_CHOICES):
                old_status = order.status
                order.status = new_status
                
                # Mettre à jour les dates spéciales
                if new_status == 'confirmed' and not order.confirmed_at:
                    order.confirmed_at = timezone.now()
                elif new_status == 'delivered' and not order.delivered_at:
                    order.delivered_at = timezone.now()
                
                order.save()
                
                # Log de l'activité
                ActivityLog.objects.create(
                    agent=request.user,
                    action='order_confirmed' if new_status == 'confirmed' else f'order_{new_status}',
                    description=f'Commande {order.order_number} passée de "{old_status}" à "{new_status}"',
                    order_id=order.id
                )
                
                messages.success(request, f'Statut de la commande mis à jour: {order.get_status_display()}')
        
        elif action == 'assign_agent':
            order.assigned_agent = request.user
            order.save()
            
            ActivityLog.objects.create(
                agent=request.user,
                action='order_assigned',
                description=f'Commande {order.order_number} assignée à {request.user.get_full_name()}',
                order_id=order.id
            )
            
            messages.success(request, 'Commande assignée avec succès.')
        
        return redirect('backoffice:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'backoffice/order_detail.html', context)

@login_required
def products_list(request):
    """Liste des produits"""
    products = Product.objects.order_by('name')
    
    # Filtres
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    low_stock = request.GET.get('low_stock')
    if low_stock:
        products = products.filter(stock_quantity__lte=5)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'low_stock': low_stock,
    }
    
    return render(request, 'backoffice/products_list.html', context)

@login_required
def update_stock(request):
    """Mise à jour du stock d'un produit (AJAX)"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock = request.POST.get('stock')
        
        try:
            product = Product.objects.get(id=product_id)
            old_stock = product.stock_quantity
            product.stock_quantity = int(new_stock)
            product.save()
            
            # Log de l'activité
            ActivityLog.objects.create(
                agent=request.user,
                action='stock_updated',
                description=f'Stock de "{product.name}" mis à jour: {old_stock} → {new_stock}',
                product_id=product.id
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Stock de {product.name} mis à jour'
            })
            
        except (Product.DoesNotExist, ValueError):
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la mise à jour du stock'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

import openpyxl
from django.http import HttpResponse


def export_clients_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clients"

    # En-têtes
    headers = ['ID', 'Nom complet', 'Téléphone', 'Quartier', 'Nb Commandes', 'Total Dépensé', 'Dernière Commande']
    ws.append(headers)

    for client in Client.objects.all():
        nb_commandes = client.order_set.count()
        total_depense = sum(order.total_amount for order in client.order_set.all())
        derniere_commande = client.order_set.order_by('-created_at').first()
        derniere_commande_date = derniere_commande.created_at.strftime("%d/%m/%Y %H:%M") if derniere_commande else "Aucune"

        row = [
            client.id,
            f"{client.first_name} {client.last_name}",
            client.phone_number,
            client.neighborhood,
            nb_commandes,
            total_depense,
            derniere_commande_date,
        ]
        ws.append(row)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=clients.xlsx'
    wb.save(response)
    return response

def order_delete(request, pk):
    if request.method == "POST":
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        messages.success(request, "La commande a été supprimée avec succès.")
        return redirect('backoffice:orders_list')
    else:
        messages.error(request, "Méthode non autorisée.")
        return redirect('backoffice:orders_list')
    
from django.db.models import Count, Sum, Max

@login_required
def clients_list(request):
    search = request.GET.get('search', '')

    clients = Client.objects.all()

    if search:
        clients = clients.filter(full_name__icontains=search)

    # Annoter les infos supplémentaires sur chaque client
    clients = clients.annotate(
        orders_count=Count('order'),
        total_spent=Sum('order__total_amount'),
        last_order_date=Max('order__created_at')
    )

    paginator = Paginator(clients, 10)  # 10 clients par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # === Statistiques des clients ===
    total_clients = Client.objects.count()

    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_clients = Client.objects.filter(created_at__gte=thirty_days_ago).count()

    seven_days_ago = timezone.now() - timedelta(days=7)
    new_clients = Client.objects.filter(created_at__gte=seven_days_ago).count()

    context = {
        'page_obj': page_obj,
        'search': search,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'new_clients': new_clients,
    }

    return render(request, 'backoffice/clients_list.html', context)


# @login_required
# def clients_list(request):
#     """Liste des clients"""
#     clients = Client.objects.annotate(
#         orders_count=Count('order')
#     ).order_by('-orders_count')
    
#     # Recherche
#     search = request.GET.get('search')
#     if search:
#         clients = clients.filter(
#             Q(first_name__icontains=search) |
#             Q(last_name__icontains=search) |
#             Q(phone_number__icontains=search) |
#             Q(neighborhood__icontains=search)
#         )
    
#     # Pagination
#     paginator = Paginator(clients, 20)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         'page_obj': page_obj,
#         'search': search,
#     }
    
#     return render(request, 'backoffice/clients_list.html', context)

@login_required
def client_detail(request, client_id):
    """Détail d'un client"""
    client = get_object_or_404(Client, id=client_id)
    orders = client.order_set.order_by('-created_at')
    
    # Statistiques du client
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'client': client,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'backoffice/client_detail.html', context)

@login_required
def activity_log(request):
    """Journal d'activité"""
    logs = ActivityLog.objects.select_related('agent').order_by('-timestamp')
    
    # Filtres
    agent_filter = request.GET.get('agent')
    if agent_filter:
        logs = logs.filter(agent_id=agent_filter)
    
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Agents pour le filtre
    from django.contrib.auth.models import User
    agents = User.objects.filter(agentprofile__is_active=True)
    
    context = {
        'page_obj': page_obj,
        'agents': agents,
        'agent_filter': agent_filter,
        'action_filter': action_filter,
        'action_choices': ActivityLog.ACTION_CHOICES,
    }
    
    return render(request, 'backoffice/activity_log.html', context)


@login_required
def generate_receipt(request, order_id):
    """Génère et télécharge le reçu de livraison"""
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que la commande est confirmée
    if order.status not in ['confirmed', 'preparing', 'ready', 'delivered']:
        messages.error(request, 'Le reçu ne peut être généré que pour les commandes confirmées.')
        return redirect('backoffice:order_detail', order_id=order_id)
    
    # Log de l'activité
    ActivityLog.objects.create(
        agent=request.user,
        action='receipt_generated',
        description=f'Reçu généré pour la commande {order.order_number}',
        order_id=order.id
    )
    
    # Importer et utiliser la fonction de génération de reçu
    from orders.utils import generate_receipt_response
    return generate_receipt_response(order)



@login_required
def agents_list(request):
    """Liste des agents (accessible aux administrateurs uniquement)"""
    # Vérifier les permissions
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agentprofile') and request.user.agentprofile.can_manage_agents)):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('backoffice:dashboard')
    
    agents = User.objects.filter(agentprofile__isnull=False).select_related('agentprofile').order_by('username')
    
    # Recherche
    search = request.GET.get('search')
    if search:
        agents = agents.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(agents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'backoffice/agents_list.html', context)

@login_required
def agent_create(request):
    """Créer un nouvel agent (accessible aux administrateurs uniquement)"""
    # Vérifier les permissions
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agentprofile') and request.user.agentprofile.can_manage_agents)):
        messages.error(request, 'Vous n\'avez pas les permissions pour créer des agents.')
        return redirect('backoffice:dashboard')
    
    if request.method == 'POST':
        form = AgentCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log de l'activité
            ActivityLog.objects.create(
                agent=request.user,
                action='agent_created',
                description=f'Nouvel agent créé: {user.get_full_name()} ({user.username})'
            )
            
            messages.success(request, f'Agent {user.get_full_name()} créé avec succès.')
            return redirect('backoffice:agents_list')
    else:
        form = AgentCreationForm()
    
    context = {
        'form': form,
        'title': 'Créer un nouvel agent'
    }
    
    return render(request, 'backoffice/agent_form.html', context)

@login_required
def agent_update(request, agent_id):
    """Modifier un agent existant (accessible aux administrateurs uniquement)"""
    # Vérifier les permissions
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agentprofile') and request.user.agentprofile.can_manage_agents)):
        messages.error(request, 'Vous n\'avez pas les permissions pour modifier des agents.')
        return redirect('backoffice:dashboard')
    
    agent_user = get_object_or_404(User, id=agent_id)
    agent_profile = get_object_or_404(AgentProfile, user=agent_user)
    
    if request.method == 'POST':
        form = AgentUpdateForm(request.POST, instance=agent_profile)
        if form.is_valid():
            form.save()
            
            # Log de l'activité
            ActivityLog.objects.create(
                agent=request.user,
                action='agent_updated',
                description=f'Agent modifié: {agent_user.get_full_name()} ({agent_user.username})'
            )
            
            messages.success(request, f'Agent {agent_user.get_full_name()} modifié avec succès.')
            return redirect('backoffice:agents_list')
    else:
        form = AgentUpdateForm(instance=agent_profile)
    
    context = {
        'form': form,
        'agent_user': agent_user,
        'title': f'Modifier l\'agent {agent_user.get_full_name()}'
    }
    
    return render(request, 'backoffice/agent_form.html', context)

@login_required
def agent_toggle_status(request, agent_id):
    """Activer/désactiver un agent (AJAX)"""
    # Vérifier les permissions
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agentprofile') and request.user.agentprofile.can_manage_agents)):
        return JsonResponse({'success': False, 'message': 'Permissions insuffisantes'})
    
    if request.method == 'POST':
        try:
            agent_user = User.objects.get(id=agent_id)
            agent_profile = agent_user.agentprofile
            
            # Ne pas permettre de se désactiver soi-même
            if agent_user == request.user:
                return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas vous désactiver vous-même'})
            
            agent_profile.is_active = not agent_profile.is_active
            agent_profile.save()
            
            # Log de l'activité
            ActivityLog.objects.create(
                agent=request.user,
                action='agent_updated',
                description=f'Agent {"activé" if agent_profile.is_active else "désactivé"}: {agent_user.get_full_name()}'
            )
            
            return JsonResponse({
                'success': True,
                'is_active': agent_profile.is_active,
                'message': f'Agent {"activé" if agent_profile.is_active else "désactivé"} avec succès'
            })
            
        except (User.DoesNotExist, AgentProfile.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Agent non trouvé'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

# views.py



