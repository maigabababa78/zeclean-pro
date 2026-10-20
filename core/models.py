from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_SUPERVISOR = 'SUPERVISOR'
    ROLE_AGENT = 'AGENT'
    ROLE_CLIENT = 'CLIENT'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrateur / Gérant'),
        (ROLE_SUPERVISOR, "Chef d'équipe / Superviseur"),
        (ROLE_AGENT, "Agent d'entretien"),
        (ROLE_CLIENT, 'Client'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_AGENT, verbose_name="Rôle")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    job_title = models.CharField(max_length=100, blank=True, verbose_name="Poste / Fonction")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=0, default=1500, verbose_name="Taux horaire (FCFA)")
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=0, default=150000, verbose_name="Salaire mensuel (FCFA)")
    hire_date = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    specialties = models.CharField(max_length=255, blank=True, verbose_name="Spécialités (ex: Vitrerie, Décapage, Bio-nettoyage)")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")

    class Meta:
        verbose_name = "Utilisateur / Collaborateur"
        verbose_name_plural = "Utilisateurs & Collaborateurs"

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name or self.username} ({self.get_role_display()})"

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de l'équipe")
    supervisor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='supervised_teams', verbose_name="Chef d'équipe"
    )
    members = models.ManyToManyField(User, related_name='teams', blank=True, verbose_name="Agents membres")
    vehicle = models.CharField(max_length=100, blank=True, verbose_name="Véhicule attribué")
    zone = models.CharField(max_length=100, blank=True, verbose_name="Zone géographique")

    class Meta:
        verbose_name = "Équipe d'intervention"
        verbose_name_plural = "Équipes d'intervention"

    def __str__(self):
        return self.name


class Client(models.Model):
    TYPE_COMPANY = 'ENTREPRISE'
    TYPE_SYNDIC = 'IMMEUBLE'
    TYPE_INDUSTRIAL = 'INDUSTRIEL'
    TYPE_MEDICAL = 'MEDICAL'
    TYPE_INDIVIDUAL = 'PARTICULIER'

    TYPE_CHOICES = [
        (TYPE_COMPANY, 'Bureaux & Entreprise'),
        (TYPE_SYNDIC, 'Syndic / Immeuble & Résidence'),
        (TYPE_INDUSTRIAL, 'Site Industriel / Entrepôt'),
        (TYPE_MEDICAL, 'Clinique / Laboratoire / Médical'),
        (TYPE_INDIVIDUAL, 'Particulier / Villa'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='client_profile', verbose_name="Compte portail client"
    )
    name = models.CharField(max_length=150, verbose_name="Nom / Raison sociale")
    client_type = models.CharField(max_length=25, choices=TYPE_CHOICES, default=TYPE_COMPANY, verbose_name="Type de client")
    contact_person = models.CharField(max_length=100, verbose_name="Interlocuteur principal")
    phone = models.CharField(max_length=30, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=255, verbose_name="Adresse du siège")
    city = models.CharField(max_length=100, default="Dakar", verbose_name="Ville")
    tax_id = models.CharField(max_length=80, blank=True, verbose_name="NINEA / RCCM / Identifiant fiscal")
    notes = models.TextField(blank=True, verbose_name="Notes internes")
    is_active = models.BooleanField(default=True, verbose_name="Client actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_client_type_display()})"


class Site(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites', verbose_name="Client")
    name = models.CharField(max_length=150, verbose_name="Nom du site")
    address = models.CharField(max_length=255, verbose_name="Adresse exacte")
    city = models.CharField(max_length=100, default="Dakar", verbose_name="Ville / Quartier")
    surface_m2 = models.PositiveIntegerField(default=100, verbose_name="Surface (m²)")
    access_instructions = models.TextField(blank=True, verbose_name="Consignes d'accès (badge, digicode, gardien)")
    contact_on_site = models.CharField(max_length=100, blank=True, verbose_name="Contact sur site")
    contact_phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone sur site")

    class Meta:
        verbose_name = "Site d'intervention"
        verbose_name_plural = "Sites d'intervention"

    def __str__(self):
        return f"{self.name} - {self.client.name} ({self.surface_m2} m²)"


class Contract(models.Model):
    FREQ_DAILY = 'QUOTIDIEN'
    FREQ_WEEKLY = 'HEBDOMADAIRE'
    FREQ_BIWEEKLY = 'BIMENSUEL'
    FREQ_MONTHLY = 'MENSUEL'
    FREQ_ONEOFF = 'PONCTUEL'

    FREQ_CHOICES = [
        (FREQ_DAILY, 'Quotidien (Lun - Sam)'),
        (FREQ_WEEKLY, 'Hebdomadaire'),
        (FREQ_BIWEEKLY, 'Bimensuel'),
        (FREQ_MONTHLY, 'Mensuel'),
        (FREQ_ONEOFF, 'Prestation ponctuelle'),
    ]

    STATUS_ACTIVE = 'ACTIF'
    STATUS_SUSPENDED = 'SUSPENDU'
    STATUS_EXPIRED = 'TERMINE'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Actif'),
        (STATUS_SUSPENDED, 'Suspendu'),
        (STATUS_EXPIRED, 'Terminé'),
    ]

    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence contrat")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts', verbose_name="Client")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='contracts', verbose_name="Site")
    title = models.CharField(max_length=200, verbose_name="Intitulé du contrat")
    frequency = models.CharField(max_length=20, choices=FREQ_CHOICES, default=FREQ_DAILY, verbose_name="Fréquence")
    monthly_amount_ht = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Montant mensuel HT (FCFA)")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name="Statut")
    sla_description = models.TextField(blank=True, verbose_name="Cahier des charges / Engagements")

    class Meta:
        verbose_name = "Contrat de nettoyage"
        verbose_name_plural = "Contrats de nettoyage"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.reference} - {self.client.name}"


class Intervention(models.Model):
    TYPE_REGULAR = 'ENTRETIEN_REGULIER'
    TYPE_DEEP = 'GRAND_MENAGE'
    TYPE_WINDOWS = 'VITRERIE'
    TYPE_DISINFECTION = 'DESINFECTION_3D'
    TYPE_CONSTRUCTION = 'FIN_CHANTIER'
    TYPE_FLOOR = 'DECAPAGE_SOL'

    TYPE_CHOICES = [
        (TYPE_REGULAR, 'Entretien régulier & Bureaux'),
        (TYPE_DEEP, 'Grand ménage approfondi'),
        (TYPE_WINDOWS, 'Nettoyage vitrerie en hauteur'),
        (TYPE_DISINFECTION, 'Désinfection / Dératisation / Désinsectisation (3D)'),
        (TYPE_CONSTRUCTION, 'Remise en état fin de chantier'),
        (TYPE_FLOOR, 'Décapage & Cristallisation des sols'),
    ]

    STATUS_PLANNED = 'PLANIFIE'
    STATUS_IN_PROGRESS = 'EN_COURS'
    STATUS_COMPLETED = 'TERMINE'
    STATUS_CANCELLED = 'ANNULE'

    STATUS_CHOICES = [
        (STATUS_PLANNED, 'Planifié'),
        (STATUS_IN_PROGRESS, 'En cours'),
        (STATUS_COMPLETED, 'Terminé'),
        (STATUS_CANCELLED, 'Annulé'),
    ]

    PRIORITY_NORMAL = 'NORMALE'
    PRIORITY_HIGH = 'HAUTE'
    PRIORITY_URGENT = 'URGENTE'

    PRIORITY_CHOICES = [
        (PRIORITY_NORMAL, 'Normale'),
        (PRIORITY_HIGH, 'Haute'),
        (PRIORITY_URGENT, 'Urgente'),
    ]

    code = models.CharField(max_length=40, unique=True, verbose_name="N° Intervention")
    title = models.CharField(max_length=200, verbose_name="Titre de la mission")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='interventions', verbose_name="Site d'intervention")
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='interventions', verbose_name="Contrat lié")
    intervention_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_REGULAR, verbose_name="Type de prestation")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='interventions', verbose_name="Équipe assignée")
    agents = models.ManyToManyField(User, related_name='assigned_interventions', blank=True, verbose_name="Agents assignés")
    scheduled_date = models.DateField(default=timezone.now, verbose_name="Date prévue")
    start_time = models.TimeField(default='08:00', verbose_name="Heure de début")
    end_time = models.TimeField(default='12:00', verbose_name="Heure de fin")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED, verbose_name="Statut")
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, verbose_name="Priorité")
    instructions = models.TextField(blank=True, verbose_name="Instructions spécifiques")
    check_in_time = models.DateTimeField(null=True, blank=True, verbose_name="Pointage arrivée")
    check_out_time = models.DateTimeField(null=True, blank=True, verbose_name="Pointage départ")
    completion_notes = models.TextField(blank=True, verbose_name="Rapport de fin de mission")
    client_rating = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Note client (/5)")
    client_feedback = models.TextField(blank=True, verbose_name="Commentaire client")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"
        ordering = ['-scheduled_date', 'start_time']

    def __str__(self):
        return f"{self.code} - {self.title} ({self.site.name})"

    @property
    def checklist_progress(self):
        total = self.tasks.count()
        if total == 0:
            return 100 if self.status == self.STATUS_COMPLETED else 0
        done = self.tasks.filter(is_completed=True).count()
        return int((done / total) * 100)


class ChecklistTask(models.Model):
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='tasks', verbose_name="Intervention")
    zone_name = models.CharField(max_length=100, default="Général", verbose_name="Zone (ex: Accueil, Sanitaires, Bureaux)")
    description = models.CharField(max_length=255, verbose_name="Tâche à contrôler")
    is_completed = models.BooleanField(default=False, verbose_name="Effectué")
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Validé par")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")

    class Meta:
        verbose_name = "Tâche de checklist"
        verbose_name_plural = "Tâches de checklist"

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"[{status}] {self.zone_name}: {self.description}"


class QualityInspection(models.Model):
    intervention = models.OneToOneField(Intervention, on_delete=models.CASCADE, related_name='quality_inspection', verbose_name="Intervention")
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Inspecteur / Superviseur")
    score_cleanliness = models.PositiveSmallIntegerField(default=90, verbose_name="Propreté visuelle (/100)")
    score_protocol = models.PositiveSmallIntegerField(default=95, verbose_name="Respect protocole & sécurité (/100)")
    score_punctuality = models.PositiveSmallIntegerField(default=100, verbose_name="Ponctualité & tenue (/100)")
    observations = models.TextField(blank=True, verbose_name="Observations & Actions correctives")
    client_signed = models.BooleanField(default=True, verbose_name="Signé et validé par le client")
    client_signatory_name = models.CharField(max_length=100, blank=True, verbose_name="Nom du signataire client")
    inspected_at = models.DateTimeField(default=timezone.now, verbose_name="Date du contrôle")

    class Meta:
        verbose_name = "Contrôle qualité"
        verbose_name_plural = "Contrôles qualité"

    @property
    def overall_score(self):
        return round((self.score_cleanliness + self.score_protocol + self.score_punctuality) / 3)

    def __str__(self):
        return f"Contrôle {self.intervention.code} - {self.overall_score}%"


class Attendance(models.Model):
    STATUS_PRESENT = 'PRESENT'
    STATUS_LATE = 'RETARD'
    STATUS_LEAVE = 'CONGE'
    STATUS_ABSENT = 'ABSENT'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Présent'),
        (STATUS_LATE, 'En retard'),
        (STATUS_LEAVE, 'En congé'),
        (STATUS_ABSENT, 'Absent'),
    ]

    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', verbose_name="Agent")
    date = models.DateField(default=timezone.now, verbose_name="Date")
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Site affecté")
    check_in = models.TimeField(null=True, blank=True, verbose_name="Heure d'arrivée")
    check_out = models.TimeField(null=True, blank=True, verbose_name="Heure de départ")
    hours_worked = models.DecimalField(max_digits=4, decimal_places=1, default=8.0, verbose_name="Heures travaillées")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PRESENT, verbose_name="Statut")
    notes = models.CharField(max_length=200, blank=True, verbose_name="Remarque")

    class Meta:
        verbose_name = "Pointage / Présence"
        verbose_name_plural = "Pointages & Présences"
        ordering = ['-date', 'agent__last_name']

    def __str__(self):
        return f"{self.agent.get_full_name()} - {self.date} ({self.get_status_display()})"


class LeaveRequest(models.Model):
    TYPE_ANNUAL = 'CONGE_ANNUEL'
    TYPE_SICK = 'MALADIE'
    TYPE_EXCEPTIONAL = 'EXCEPTIONNEL'

    TYPE_CHOICES = [
        (TYPE_ANNUAL, 'Congé payé annuel'),
        (TYPE_SICK, 'Arrêt maladie'),
        (TYPE_EXCEPTIONAL, 'Permission exceptionnelle'),
    ]

    STATUS_PENDING = 'EN_ATTENTE'
    STATUS_APPROVED = 'APPROUVE'
    STATUS_REJECTED = 'REFUSE'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_APPROVED, 'Approuvé'),
        (STATUS_REJECTED, 'Refusé'),
    ]

    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests', verbose_name="Collaborateur")
    leave_type = models.CharField(max_length=25, choices=TYPE_CHOICES, default=TYPE_ANNUAL, verbose_name="Type de congé")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    reason = models.TextField(blank=True, verbose_name="Motif")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="Statut")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves', verbose_name="Validé par")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Demande de congé"
        verbose_name_plural = "Demandes de congés"
        ordering = ['-created_at']

    @property
    def duration_days(self):
        return max((self.end_date - self.start_date).days + 1, 1)


class InventoryItem(models.Model):
    CAT_CHEMICAL = 'PRODUIT_CHIMIQUE'
    CAT_CONSUMABLE = 'CONSOMMABLE'
    CAT_MACHINE = 'MACHINE_EQUIPEMENT'
    CAT_PPE = 'EPI_SECURITE'

    CAT_CHOICES = [
        (CAT_CHEMICAL, "Produits d'entretien & Détergents"),
        (CAT_CONSUMABLE, 'Consommables (Sacs, Papier, Savon)'),
        (CAT_MACHINE, 'Machines & Matériel lourd (Autolaveuse, Monobrosse, Aspirateur)'),
        (CAT_PPE, 'EPI & Tenues de sécurité (Gants, Bottes, Masques)'),
    ]

    sku = models.CharField(max_length=40, unique=True, verbose_name="Code article")
    name = models.CharField(max_length=150, verbose_name="Désignation")
    category = models.CharField(max_length=30, choices=CAT_CHOICES, default=CAT_CHEMICAL, verbose_name="Catégorie")
    quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0, verbose_name="Quantité en stock")
    unit = models.CharField(max_length=30, default="Litre", verbose_name="Unité (Bidon 5L, Carton, Unité...)")
    min_threshold = models.DecimalField(max_digits=10, decimal_places=1, default=5, verbose_name="Seuil d'alerte")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Prix unitaire HT (FCFA)")
    supplier = models.CharField(max_length=120, blank=True, verbose_name="Fournisseur")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article en stock"
        verbose_name_plural = "Articles en stock"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_threshold

    @property
    def total_value(self):
        return int(self.quantity * self.unit_cost)


class StockMovement(models.Model):
    MOVE_IN = 'ENTREE'
    MOVE_OUT = 'SORTIE'

    MOVE_CHOICES = [
        (MOVE_IN, 'Entrée en stock (Approvisionnement)'),
        (MOVE_OUT, 'Sortie vers site / intervention'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements', verbose_name="Article")
    movement_type = models.CharField(max_length=15, choices=MOVE_CHOICES, verbose_name="Type de mouvement")
    quantity = models.DecimalField(max_digits=10, decimal_places=1, verbose_name="Quantité")
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Site destinataire")
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Effectué par")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Motif / Bon de livraison")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date")

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']


class Quote(models.Model):
    STATUS_DRAFT = 'BROUILLON'
    STATUS_SENT = 'ENVOYE'
    STATUS_ACCEPTED = 'ACCEPTE'
    STATUS_REJECTED = 'REFUSE'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Brouillon'),
        (STATUS_SENT, 'Envoyé au client'),
        (STATUS_ACCEPTED, 'Accepté & Signé'),
        (STATUS_REJECTED, 'Refusé'),
    ]

    number = models.CharField(max_length=40, unique=True, verbose_name="N° Devis")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='quotes', verbose_name="Client")
    site_name = models.CharField(max_length=150, verbose_name="Site concerné")
    surface_m2 = models.PositiveIntegerField(default=100, verbose_name="Surface estimée (m²)")
    service_description = models.TextField(verbose_name="Détail de la prestation")
    amount_ht = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Montant HT (FCFA)")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'), verbose_name="Taux TVA (%)")
    issue_date = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    valid_until = models.DateField(verbose_name="Valide jusqu'au")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT, verbose_name="Statut")

    class Meta:
        verbose_name = "Devis commercial"
        verbose_name_plural = "Devis commerciaux"
        ordering = ['-issue_date']

    @property
    def tax_amount(self):
        return int(self.amount_ht * (self.tax_rate / Decimal('100')))

    @property
    def amount_ttc(self):
        return int(self.amount_ht + self.tax_amount)

    def __str__(self):
        return f"{self.number} - {self.client.name} ({self.amount_ttc} FCFA)"


class Invoice(models.Model):
    STATUS_UNPAID = 'EN_ATTENTE'
    STATUS_PARTIAL = 'PARTIEL'
    STATUS_PAID = 'PAYEE'
    STATUS_OVERDUE = 'RETARD'

    STATUS_CHOICES = [
        (STATUS_UNPAID, 'En attente de règlement'),
        (STATUS_PARTIAL, 'Payée partiellement'),
        (STATUS_PAID, 'Payée'),
        (STATUS_OVERDUE, 'En retard de paiement'),
    ]

    METHOD_TRANSFER = 'VIREMENT'
    METHOD_CHECK = 'CHEQUE'
    METHOD_MOBILE = 'MOBILE_MONEY'
    METHOD_CASH = 'ESPECES'

    METHOD_CHOICES = [
        (METHOD_TRANSFER, 'Virement bancaire'),
        (METHOD_CHECK, 'Chèque'),
        (METHOD_MOBILE, 'Wave / Orange Money / Mobile Money'),
        (METHOD_CASH, 'Espèces'),
    ]

    number = models.CharField(max_length=40, unique=True, verbose_name="N° Facture")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', verbose_name="Client")
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name="Contrat associé")
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name="Devis d'origine")
    period_label = models.CharField(max_length=100, default="Octobre 2026", verbose_name="Période facturée / Objet")
    issue_date = models.DateField(default=timezone.now, verbose_name="Date de facturation")
    due_date = models.DateField(verbose_name="Date d'échéance")
    amount_ht = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Montant HT (FCFA)")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'), verbose_name="TVA (%)")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Montant déjà réglé (FCFA)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPAID, verbose_name="Statut")
    payment_method = models.CharField(max_length=25, choices=METHOD_CHOICES, default=METHOD_TRANSFER, verbose_name="Mode de règlement")

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-issue_date']

    @property
    def tax_amount(self):
        return int(self.amount_ht * (self.tax_rate / Decimal('100')))

    @property
    def amount_ttc(self):
        return int(self.amount_ht + self.tax_amount)

    @property
    def balance_due(self):
        return max(self.amount_ttc - int(self.amount_paid), 0)

    def __str__(self):
        return f"{self.number} - {self.client.name}"


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines', verbose_name="Facture")
    description = models.CharField(max_length=255, verbose_name="Désignation de la prestation")
    quantity = models.DecimalField(max_digits=8, decimal_places=1, default=1, verbose_name="Quantité / Forfait")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Prix unitaire HT (FCFA)")

    @property
    def line_total(self):
        return int(self.quantity * self.unit_price)

    def __str__(self):
        return f"{self.description} ({self.line_total} FCFA)"
