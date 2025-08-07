from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    # Authentification
    path('login/', views.agent_login, name='login'),
    path('logout/', views.agent_logout, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Commandes
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/receipt/', views.generate_receipt, name='generate_receipt'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    # Produits et stock
    path('products/', views.products_list, name='products_list'),
    path('update-stock/', views.update_stock, name='update_stock'),
    path('export-clients-excel/', views.export_clients_excel, name='export_clients_excel'),
    # Clients
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    
    # Agents (accessible aux administrateurs uniquement)
    path('agents/', views.agents_list, name='agents_list'),
    path('agents/create/', views.agent_create, name='agent_create'),
    path('agents/<int:agent_id>/update/', views.agent_update, name='agent_update'),
    path('agents/<int:agent_id>/toggle-status/', views.agent_toggle_status, name='agent_toggle_status'),
    
    # Journal d'activité
    path('activity/', views.activity_log, name='activity_log'),
    
    
]