from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.http import JsonResponse
from .models import (
    User, Team, Client, Site, Contract, Intervention,
    ChecklistTask, QualityInspection, Attendance, LeaveRequest,
    InventoryItem, StockMovement, Quote, Invoice, InvoiceLine
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants incorrects. Vous pouvez aussi utiliser les boutons de connexion rapide ci-dessous.")
    demo_accounts = User.objects.filter(username__in=['admin', 'superviseur', 'agent', 'client']).order_by('id')
    return render(request, 'core/login.html', {'demo_accounts': demo_accounts})


def quick_login_view(request, role_slug):
    """Connexion instantanée en 1 clic pour tester les 4 profils (Admin, Superviseur, Agent, Client)."""
    mapping = {
        'admin': 'admin',
        'superviseur': 'superviseur',
        'agent': 'agent',
        'client': 'client',
    }
    username = mapping.get(role_slug, 'admin')
    user = User.objects.filter(username=username).first()
    if user:
        login(request, user)
        messages.info(request, f"Connecté en tant que : {user.get_full_name()} ({user.get_role_display()})")
        return redirect('dashboard')
    messages.error(request, "Compte de démonstration introuvable.")
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    today = timezone.localdate()
    user = request.user

    # Filtrage intelligent selon le profil connecté
    if user.role == User.ROLE_CLIENT and hasattr(user, 'client_profile') and user.client_profile:
        client = user.client_profile
        interventions_qs = Intervention.objects.filter(site__client=client)
        invoices_qs = Invoice.objects.filter(client=client)
    elif user.role == User.ROLE_AGENT:
        interventions_qs = Intervention.objects.filter(Q(agents=user) | Q(team__members=user)).distinct()
        invoices_qs = Invoice.objects.none()
    else:
        interventions_qs = Intervention.objects.all()
        invoices_qs = Invoice.objects.all()

    # Statistiques globales
    active_clients_count = Client.objects.filter(is_active=True).count()
    active_contracts = Contract.objects.filter(status=Contract.STATUS_ACTIVE)
    monthly_recurring_ht = active_contracts.aggregate(total=Sum('monthly_amount_ht'))['total'] or 0

    today_interventions = interventions_qs.filter(scheduled_date=today).select_related('site', 'site__client', 'team')
    upcoming_interventions = interventions_qs.filter(scheduled_date__gte=today).select_related('site', 'site__client', 'team')[:8]

    completed_count = interventions_qs.filter(status=Intervention.STATUS_COMPLETED).count()
    in_progress_count = interventions_qs.filter(status=Intervention.STATUS_IN_PROGRESS).count()
    planned_count = interventions_qs.filter(status=Intervention.STATUS_PLANNED).count()

    # Chiffre d'affaires & Facturation
    total_billed_ht = invoices_qs.aggregate(total=Sum('amount_ht'))['total'] or 0
    total_paid = invoices_qs.aggregate(total=Sum('amount_paid'))['total'] or 0
    unpaid_invoices = invoices_qs.exclude(status=Invoice.STATUS_PAID)

    # Qualité moyenne
    inspections = QualityInspection.objects.all()
    if inspections.exists():
        avg_quality = round(sum(i.overall_score for i in inspections) / inspections.count())
    else:
        avg_quality = 94

    # Alertes stock
    all_items = InventoryItem.objects.all()
    low_stock_items = [item for item in all_items if item.is_low_stock]

    # Agents disponibles
    agents_total = User.objects.filter(role__in=[User.ROLE_AGENT, User.ROLE_SUPERVISOR]).count()
    agents_present_today = Attendance.objects.filter(date=today, status__in=[Attendance.STATUS_PRESENT, Attendance.STATUS_LATE]).count()

    context = {
        'page_title': 'Tableau de bord',
        'today': today,
        'active_clients_count': active_clients_count,
        'active_contracts_count': active_contracts.count(),
        'monthly_recurring_ht': monthly_recurring_ht,
        'today_interventions': today_interventions,
        'upcoming_interventions': upcoming_interventions,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'planned_count': planned_count,
        'total_billed_ht': total_billed_ht,
        'total_paid': total_paid,
        'unpaid_invoices_count': unpaid_invoices.count(),
        'avg_quality': avg_quality,
        'low_stock_items': low_stock_items,
        'agents_total': agents_total,
        'agents_present_today': agents_present_today,
        'recent_inspections': QualityInspection.objects.select_related('intervention', 'intervention__site', 'inspector').order_by('-inspected_at')[:4],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def clients_view(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'create_client')
        if action == 'create_client':
            client = Client.objects.create(
                name=request.POST.get('name'),
                client_type=request.POST.get('client_type', Client.TYPE_COMPANY),
                contact_person=request.POST.get('contact_person'),
                phone=request.POST.get('phone'),
                email=request.POST.get('email', 'contact@client.sn'),
                address=request.POST.get('address'),
                city=request.POST.get('city', 'Dakar'),
                tax_id=request.POST.get('tax_id', ''),
                notes=request.POST.get('notes', ''),
            )
            # Création optionnelle du premier site associé
            site_name = request.POST.get('site_name', '').strip()
            if site_name:
                Site.objects.create(
                    client=client,
                    name=site_name,
                    address=request.POST.get('address'),
                    city=request.POST.get('city', 'Dakar'),
                    surface_m2=int(request.POST.get('surface_m2') or 250),
                    access_instructions=request.POST.get('access_instructions', ''),
                    contact_on_site=request.POST.get('contact_person'),
                    contact_phone=request.POST.get('phone'),
                )
            messages.success(request, f"Le client « {client.name} » a été ajouté avec succès.")
            return redirect('clients')

        elif action == 'create_site':
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, id=client_id)
            site = Site.objects.create(
                client=client,
                name=request.POST.get('name'),
                address=request.POST.get('address'),
                city=request.POST.get('city', 'Dakar'),
                surface_m2=int(request.POST.get('surface_m2') or 200),
                access_instructions=request.POST.get('access_instructions', ''),
                contact_on_site=request.POST.get('contact_on_site', client.contact_person),
                contact_phone=request.POST.get('contact_phone', client.phone),
            )
            messages.success(request, f"Le site « {site.name} » a été rattaché à {client.name}.")
            return redirect('clients')

        elif action == 'create_contract':
            site = get_object_or_404(Site, id=request.POST.get('site_id'))
            count = Contract.objects.count() + 1
            Contract.objects.create(
                reference=f"CTR-2026-{count:03d}",
                client=site.client,
                site=site,
                title=request.POST.get('title'),
                frequency=request.POST.get('frequency', Contract.FREQ_DAILY),
                monthly_amount_ht=Decimal(request.POST.get('monthly_amount_ht') or '250000'),
                start_date=request.POST.get('start_date') or timezone.localdate(),
                sla_description=request.POST.get('sla_description', ''),
            )
            messages.success(request, f"Nouveau contrat créé pour {site.client.name}.")
            return redirect('clients')

    search_q = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()

    clients = Client.objects.prefetch_related('sites', 'contracts').all()
    if search_q:
        clients = clients.filter(
            Q(name__icontains=search_q) |
            Q(contact_person__icontains=search_q) |
            Q(city__icontains=search_q) |
            Q(phone__icontains=search_q)
        )
    if type_filter:
        clients = clients.filter(client_type=type_filter)

    sites = Site.objects.select_related('client').all()
    contracts = Contract.objects.select_related('client', 'site').all()

    return render(request, 'core/clients.html', {
        'page_title': 'Clients, Sites & Contrats',
        'clients': clients,
        'sites': sites,
        'contracts': contracts,
        'client_types': Client.TYPE_CHOICES,
        'frequencies': Contract.FREQ_CHOICES,
        'search_q': search_q,
        'type_filter': type_filter,
    })


@login_required
def planning_view(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'create_intervention')
        if action == 'create_intervention':
            site = get_object_or_404(Site, id=request.POST.get('site_id'))
            team_id = request.POST.get('team_id')
            team = Team.objects.filter(id=team_id).first() if team_id else None
            count = Intervention.objects.count() + 1
            intervention = Intervention.objects.create(
                code=f"INT-2026-{count:03d}",
                title=request.POST.get('title'),
                site=site,
                intervention_type=request.POST.get('intervention_type', Intervention.TYPE_REGULAR),
                team=team,
                scheduled_date=request.POST.get('scheduled_date') or timezone.localdate(),
                start_time=request.POST.get('start_time') or '08:00',
                end_time=request.POST.get('end_time') or '12:00',
                priority=request.POST.get('priority', Intervention.PRIORITY_NORMAL),
                instructions=request.POST.get('instructions', ''),
            )
            if team:
                intervention.agents.set(team.members.all())

            # Génération automatique d'une checklist adaptée au type d'intervention
            default_tasks = [
                ("Accueil & Bureaux", "Dépoussiérage complet des postes de travail et mobilier"),
                ("Accueil & Bureaux", "Vidage des corbeilles et remplacement des sacs poubelles"),
                ("Sols & Circulations", "Aspiration et lavage humide désinfectant des sols"),
                ("Sanitaires", "Nettoyage, détartrage et désinfection des blocs sanitaires"),
                ("Vitrerie & Entrée", "Nettoyage des portes vitrées et miroirs sans traces"),
            ]
            for zone, desc in default_tasks:
                ChecklistTask.objects.create(
                    intervention=intervention,
                    zone_name=zone,
                    description=desc
                )
            messages.success(request, f"Intervention {intervention.code} planifiée avec sa checklist qualité.")
            return redirect('planning')

    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    date_filter = request.GET.get('date', '')

    interventions = Intervention.objects.select_related('site', 'site__client', 'team').prefetch_related('agents', 'tasks').all()

    if request.user.role == User.ROLE_AGENT:
        interventions = interventions.filter(Q(agents=request.user) | Q(team__members=request.user)).distinct()
    elif request.user.role == User.ROLE_CLIENT and hasattr(request.user, 'client_profile') and request.user.client_profile:
        interventions = interventions.filter(site__client=request.user.client_profile)

    if status_filter:
        interventions = interventions.filter(status=status_filter)
    if type_filter:
        interventions = interventions.filter(intervention_type=type_filter)
    if date_filter:
        interventions = interventions.filter(scheduled_date=date_filter)

    return render(request, 'core/planning.html', {
        'page_title': 'Planning des Interventions',
        'interventions': interventions,
        'sites': Site.objects.select_related('client').all(),
        'teams': Team.objects.prefetch_related('members').all(),
        'intervention_types': Intervention.TYPE_CHOICES,
        'statuses': Intervention.STATUS_CHOICES,
        'priorities': Intervention.PRIORITY_CHOICES,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'date_filter': date_filter,
    })


@login_required
def intervention_detail_view(request, pk):
    intervention = get_object_or_404(
        Intervention.objects.select_related('site', 'site__client', 'team', 'contract').prefetch_related('tasks', 'agents'),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            new_status = request.POST.get('status')
            intervention.status = new_status
            if new_status == Intervention.STATUS_IN_PROGRESS and not intervention.check_in_time:
                intervention.check_in_time = timezone.now()
            elif new_status == Intervention.STATUS_COMPLETED:
                intervention.check_out_time = timezone.now()
                intervention.completion_notes = request.POST.get('completion_notes', intervention.completion_notes)
            intervention.save()
            messages.success(request, f"Statut de l'intervention mis à jour : {intervention.get_status_display()}.")

        elif action == 'toggle_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(ChecklistTask, id=task_id, intervention=intervention)
            task.is_completed = not task.is_completed
            task.completed_by = request.user if task.is_completed else None
            task.completed_at = timezone.now() if task.is_completed else None
            task.save()
            if request.headers.get('HX-Request'):
                return render(request, 'core/partials/checklist_box.html', {'intervention': intervention})

        elif action == 'add_task':
            zone_name = request.POST.get('zone_name', 'Général')
            description = request.POST.get('description', '').strip()
            if description:
                ChecklistTask.objects.create(
                    intervention=intervention,
                    zone_name=zone_name,
                    description=description
                )
                messages.success(request, "Point de contrôle ajouté à la checklist.")

        elif action == 'save_inspection':
            QualityInspection.objects.update_or_create(
                intervention=intervention,
                defaults={
                    'inspector': request.user,
                    'score_cleanliness': int(request.POST.get('score_cleanliness') or 95),
                    'score_protocol': int(request.POST.get('score_protocol') or 95),
                    'score_punctuality': int(request.POST.get('score_punctuality') or 100),
                    'observations': request.POST.get('observations', ''),
                    'client_signed': request.POST.get('client_signed') == 'on',
                    'client_signatory_name': request.POST.get('client_signatory_name', intervention.site.contact_on_site),
                }
            )
            intervention.status = Intervention.STATUS_COMPLETED
            if not intervention.check_out_time:
                intervention.check_out_time = timezone.now()
            intervention.save()
            messages.success(request, "Contrôle qualité enregistré et intervention clôturée !")

        return redirect('intervention_detail', pk=intervention.pk)

    return render(request, 'core/intervention_detail.html', {
        'page_title': f"Intervention {intervention.code}",
        'intervention': intervention,
    })


@login_required
def staff_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_agent':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            username = request.POST.get('username', '').strip() or f"{first_name.lower()}.{last_name.lower()}".replace(' ', '')
            if User.objects.filter(username=username).exists():
                username = f"{username}{User.objects.count() + 1}"
            agent = User.objects.create_user(
                username=username,
                password='password123',
                first_name=first_name,
                last_name=last_name,
                role=request.POST.get('role', User.ROLE_AGENT),
                phone=request.POST.get('phone', ''),
                job_title=request.POST.get('job_title', 'Agent de propreté qualifié'),
                monthly_salary=Decimal(request.POST.get('monthly_salary') or '150000'),
                hourly_rate=Decimal(request.POST.get('hourly_rate') or '1500'),
                specialties=request.POST.get('specialties', 'Entretien bureaux, Vitrerie'),
                hire_date=request.POST.get('hire_date') or timezone.localdate(),
            )
            team_id = request.POST.get('team_id')
            if team_id:
                team = Team.objects.filter(id=team_id).first()
                if team:
                    team.members.add(agent)
            messages.success(request, f"Collaborateur {agent.get_full_name()} ajouté avec succès.")
            return redirect('staff')

        elif action == 'create_attendance':
            agent = get_object_or_404(User, id=request.POST.get('agent_id'))
            site_id = request.POST.get('site_id')
            site = Site.objects.filter(id=site_id).first() if site_id else None
            Attendance.objects.create(
                agent=agent,
                date=request.POST.get('date') or timezone.localdate(),
                site=site,
                check_in=request.POST.get('check_in') or '07:30',
                check_out=request.POST.get('check_out') or '16:30',
                hours_worked=Decimal(request.POST.get('hours_worked') or '8.0'),
                status=request.POST.get('status', Attendance.STATUS_PRESENT),
                notes=request.POST.get('notes', ''),
            )
            messages.success(request, f"Pointage enregistré pour {agent.get_full_name()}.")
            return redirect('staff')

        elif action == 'create_leave':
            agent_id = request.POST.get('agent_id')
            agent = get_object_or_404(User, id=agent_id) if agent_id else request.user
            LeaveRequest.objects.create(
                agent=agent,
                leave_type=request.POST.get('leave_type', LeaveRequest.TYPE_ANNUAL),
                start_date=request.POST.get('start_date') or timezone.localdate(),
                end_date=request.POST.get('end_date') or (timezone.localdate() + timedelta(days=5)),
                reason=request.POST.get('reason', ''),
            )
            messages.success(request, "Demande de congé enregistrée.")
            return redirect('staff')

        elif action == 'update_leave':
            leave = get_object_or_404(LeaveRequest, id=request.POST.get('leave_id'))
            leave.status = request.POST.get('status', LeaveRequest.STATUS_APPROVED)
            leave.approved_by = request.user
            leave.save()
            messages.success(request, f"Demande de congé de {leave.agent.get_full_name()} mise à jour.")
            return redirect('staff')

    staff_members = User.objects.filter(role__in=[User.ROLE_AGENT, User.ROLE_SUPERVISOR, User.ROLE_ADMIN]).order_by('role', 'last_name')
    teams = Team.objects.select_related('supervisor').prefetch_related('members').all()
    attendances = Attendance.objects.select_related('agent', 'site').all()[:20]
    leaves = LeaveRequest.objects.select_related('agent', 'approved_by').all()[:15]
    total_payroll = staff_members.aggregate(total=Sum('monthly_salary'))['total'] or 0

    return render(request, 'core/staff.html', {
        'page_title': 'Personnel, Équipes & Pointage',
        'staff_members': staff_members,
        'teams': teams,
        'attendances': attendances,
        'leaves': leaves,
        'sites': Site.objects.all(),
        'total_payroll': total_payroll,
    })


@login_required
def billing_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_quote':
            client = get_object_or_404(Client, id=request.POST.get('client_id'))
            count = Quote.objects.count() + 1
            Quote.objects.create(
                number=f"DEV-2026-{count:03d}",
                client=client,
                site_name=request.POST.get('site_name'),
                surface_m2=int(request.POST.get('surface_m2') or 200),
                service_description=request.POST.get('service_description'),
                amount_ht=Decimal(request.POST.get('amount_ht') or '150000'),
                tax_rate=Decimal(request.POST.get('tax_rate') or '18.00'),
                issue_date=timezone.localdate(),
                valid_until=timezone.localdate() + timedelta(days=30),
                status=Quote.STATUS_SENT,
            )
            messages.success(request, "Devis créé avec succès.")
            return redirect('billing')

        elif action == 'convert_quote':
            quote = get_object_or_404(Quote, id=request.POST.get('quote_id'))
            quote.status = Quote.STATUS_ACCEPTED
            quote.save()
            count = Invoice.objects.count() + 1
            invoice = Invoice.objects.create(
                number=f"FAC-2026-{count:03d}",
                client=quote.client,
                quote=quote,
                period_label=f"Prestation : {quote.site_name} ({quote.surface_m2} m²)",
                issue_date=timezone.localdate(),
                due_date=timezone.localdate() + timedelta(days=15),
                amount_ht=quote.amount_ht,
                tax_rate=quote.tax_rate,
                status=Invoice.STATUS_UNPAID,
            )
            InvoiceLine.objects.create(
                invoice=invoice,
                description=quote.service_description,
                quantity=Decimal('1.0'),
                unit_price=quote.amount_ht,
            )
            messages.success(request, f"Devis {quote.number} accepté et transformé en facture {invoice.number} !")
            return redirect('billing')

        elif action == 'create_invoice':
            client = get_object_or_404(Client, id=request.POST.get('client_id'))
            count = Invoice.objects.count() + 1
            amount_ht = Decimal(request.POST.get('amount_ht') or '300000')
            invoice = Invoice.objects.create(
                number=f"FAC-2026-{count:03d}",
                client=client,
                period_label=request.POST.get('period_label', 'Prestation mensuelle Octobre 2026'),
                issue_date=timezone.localdate(),
                due_date=request.POST.get('due_date') or (timezone.localdate() + timedelta(days=15)),
                amount_ht=amount_ht,
                tax_rate=Decimal(request.POST.get('tax_rate') or '18.00'),
                payment_method=request.POST.get('payment_method', Invoice.METHOD_TRANSFER),
                status=Invoice.STATUS_UNPAID,
            )
            InvoiceLine.objects.create(
                invoice=invoice,
                description=invoice.period_label,
                quantity=Decimal('1.0'),
                unit_price=amount_ht,
            )
            messages.success(request, f"Facture {invoice.number} générée avec succès.")
            return redirect('billing')

        elif action == 'record_payment':
            invoice = get_object_or_404(Invoice, id=request.POST.get('invoice_id'))
            payment_amount = Decimal(request.POST.get('payment_amount') or invoice.balance_due)
            invoice.amount_paid = min(invoice.amount_paid + payment_amount, Decimal(invoice.amount_ttc))
            invoice.payment_method = request.POST.get('payment_method', invoice.payment_method)
            if invoice.amount_paid >= invoice.amount_ttc:
                invoice.status = Invoice.STATUS_PAID
            elif invoice.amount_paid > 0:
                invoice.status = Invoice.STATUS_PARTIAL
            invoice.save()
            messages.success(request, f"Règlement enregistré sur la facture {invoice.number}.")
            return redirect('billing')

    quotes = Quote.objects.select_related('client').all()
    invoices = Invoice.objects.select_related('client', 'contract', 'quote').all()

    if request.user.role == User.ROLE_CLIENT and hasattr(request.user, 'client_profile') and request.user.client_profile:
        quotes = quotes.filter(client=request.user.client_profile)
        invoices = invoices.filter(client=request.user.client_profile)

    total_invoiced_ttc = sum(inv.amount_ttc for inv in invoices)
    total_collected = sum(int(inv.amount_paid) for inv in invoices)
    total_outstanding = sum(inv.balance_due for inv in invoices)

    return render(request, 'core/billing.html', {
        'page_title': 'Devis, Facturation & Paiements (FCFA)',
        'quotes': quotes,
        'invoices': invoices,
        'clients': Client.objects.filter(is_active=True),
        'total_invoiced_ttc': total_invoiced_ttc,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'payment_methods': Invoice.METHOD_CHOICES,
    })


@login_required
def invoice_print_view(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related('client', 'contract').prefetch_related('lines'), pk=pk)
    return render(request, 'core/invoice_print.html', {
        'invoice': invoice,
        'page_title': f"Facture {invoice.number}",
    })


@login_required
def inventory_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_item':
            count = InventoryItem.objects.count() + 1
            InventoryItem.objects.create(
                sku=request.POST.get('sku') or f"ART-{count:03d}",
                name=request.POST.get('name'),
                category=request.POST.get('category', InventoryItem.CAT_CHEMICAL),
                quantity=Decimal(request.POST.get('quantity') or '10'),
                unit=request.POST.get('unit', 'Bidon 5L'),
                min_threshold=Decimal(request.POST.get('min_threshold') or '5'),
                unit_cost=Decimal(request.POST.get('unit_cost') or '8500'),
                supplier=request.POST.get('supplier', 'Sénégal Chimie Pro'),
            )
            messages.success(request, "Nouvel article ajouté à l'inventaire.")
            return redirect('inventory')

        elif action == 'stock_movement':
            item = get_object_or_404(InventoryItem, id=request.POST.get('item_id'))
            move_type = request.POST.get('movement_type', StockMovement.MOVE_OUT)
            qty = Decimal(request.POST.get('quantity') or '1')
            site_id = request.POST.get('site_id')
            site = Site.objects.filter(id=site_id).first() if site_id else None

            if move_type == StockMovement.MOVE_IN:
                item.quantity += qty
            else:
                item.quantity = max(Decimal('0'), item.quantity - qty)
            item.save()

            StockMovement.objects.create(
                item=item,
                movement_type=move_type,
                quantity=qty,
                site=site,
                performed_by=request.user,
                notes=request.POST.get('notes', ''),
            )
            messages.success(request, f"Mouvement de stock ({move_type}) enregistré pour {item.name}.")
            return redirect('inventory')

    items = InventoryItem.objects.all()
    movements = StockMovement.objects.select_related('item', 'site', 'performed_by').all()[:20]
    total_stock_value = sum(item.total_value for item in items)
    low_stock_count = sum(1 for item in items if item.is_low_stock)

    return render(request, 'core/inventory.html', {
        'page_title': 'Stocks, Produits & Équipements',
        'items': items,
        'movements': movements,
        'sites': Site.objects.select_related('client').all(),
        'categories': InventoryItem.CAT_CHOICES,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
    })


@login_required
def quality_view(request):
    if request.method == 'POST':
        intervention = get_object_or_404(Intervention, id=request.POST.get('intervention_id'))
        QualityInspection.objects.update_or_create(
            intervention=intervention,
            defaults={
                'inspector': request.user,
                'score_cleanliness': int(request.POST.get('score_cleanliness') or 92),
                'score_protocol': int(request.POST.get('score_protocol') or 95),
                'score_punctuality': int(request.POST.get('score_punctuality') or 98),
                'observations': request.POST.get('observations', ''),
                'client_signed': request.POST.get('client_signed') == 'on',
                'client_signatory_name': request.POST.get('client_signatory_name', intervention.site.contact_on_site),
            }
        )
        intervention.status = Intervention.STATUS_COMPLETED
        intervention.save()
        messages.success(request, f"Rapport d'inspection qualité enregistré pour {intervention.code}.")
        return redirect('quality')

    inspections = QualityInspection.objects.select_related(
        'intervention', 'intervention__site', 'intervention__site__client', 'inspector'
    ).order_by('-inspected_at')

    uninspected_interventions = Intervention.objects.filter(
        quality_inspection__isnull=True
    ).select_related('site', 'site__client')

    avg_cleanliness = round(inspections.aggregate(a=Avg('score_cleanliness'))['a'] or 93)
    avg_protocol = round(inspections.aggregate(a=Avg('score_protocol'))['a'] or 95)
    avg_punctuality = round(inspections.aggregate(a=Avg('score_punctuality'))['a'] or 97)

    return render(request, 'core/quality.html', {
        'page_title': 'Contrôle Qualité & Rapports Terrain',
        'inspections': inspections,
        'uninspected_interventions': uninspected_interventions,
        'avg_cleanliness': avg_cleanliness,
        'avg_protocol': avg_protocol,
        'avg_punctuality': avg_punctuality,
    })
