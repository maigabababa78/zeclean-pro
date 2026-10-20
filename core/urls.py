from django.urls import path
from . import views
from . import excel_exports

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('quick-login/<str:role_slug>/', views.quick_login_view, name='quick_login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    path('clients/', views.clients_view, name='clients'),
    path('planning/', views.planning_view, name='planning'),
    path('interventions/<int:pk>/', views.intervention_detail_view, name='intervention_detail'),
    path('personnel/', views.staff_view, name='staff'),
    path('facturation/', views.billing_view, name='billing'),
    path('facturation/facture/<int:pk>/imprimer/', views.invoice_print_view, name='invoice_print'),
    path('stocks/', views.inventory_view, name='inventory'),
    path('qualite/', views.quality_view, name='quality'),

    # Exports Excel (.xlsx)
    path('export/personnel-paie.xlsx', excel_exports.export_staff_excel, name='export_staff_excel'),
    path('export/facturation-fcfa.xlsx', excel_exports.export_billing_excel, name='export_billing_excel'),
    path('export/planning-interventions.xlsx', excel_exports.export_planning_excel, name='export_planning_excel'),
    path('export/stocks-materiel.xlsx', excel_exports.export_inventory_excel, name='export_inventory_excel'),
    path('export/clients-contrats.xlsx', excel_exports.export_clients_excel, name='export_clients_excel'),
]
