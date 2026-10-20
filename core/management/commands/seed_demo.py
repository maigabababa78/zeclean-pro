from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    User, Team, Client, Site, Contract, Intervention,
    ChecklistTask, QualityInspection, Attendance, LeaveRequest,
    InventoryItem, StockMovement, Quote, Invoice, InvoiceLine
)


class Command(BaseCommand):
    help = "Initialise la base de données avec un jeu de données complet pour une société de nettoyage (Zone CFA)"

    def handle(self, *args, **options):
        if Client.objects.exists():
            self.stdout.write(self.style.WARNING("Les données de démonstration existent déjà."))
            return

        today = timezone.localdate()

        # 1. Comptes utilisateurs principaux (4 profils demandés)
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Amadou',
                'last_name': 'Diallo',
                'email': 'direction@cleanpro-services.com',
                'role': User.ROLE_ADMIN,
                'phone': '+221 77 650 10 10',
                'job_title': 'Directeur Général',
                'monthly_salary': Decimal('650000'),
                'hourly_rate': Decimal('4500'),
                'hire_date': today - timedelta(days=900),
                'specialties': 'Direction Générale, Grands Comptes & Appels d’Offres',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        sup_user, _ = User.objects.get_or_create(
            username='superviseur',
            defaults={
                'first_name': 'Moussa',
                'last_name': 'Ndiaye',
                'email': 'm.ndiaye@cleanpro-services.com',
                'role': User.ROLE_SUPERVISOR,
                'phone': '+221 77 412 88 90',
                'job_title': 'Superviseur Technique & Qualité HSE',
                'monthly_salary': Decimal('320000'),
                'hourly_rate': Decimal('2500'),
                'hire_date': today - timedelta(days=540),
                'specialties': 'Contrôle Qualité, Bio-nettoyage, Encadrement terrain',
            }
        )
        sup_user.set_password('superviseur123')
        sup_user.save()

        sup2_user, _ = User.objects.get_or_create(
            username='fatou.sow',
            defaults={
                'first_name': 'Fatou',
                'last_name': 'Sow',
                'email': 'f.sow@cleanpro-services.com',
                'role': User.ROLE_SUPERVISOR,
                'phone': '+221 78 120 44 55',
                'job_title': "Cheffe d'Équipe Tertiaire & Résidences",
                'monthly_salary': Decimal('280000'),
                'hourly_rate': Decimal('2200'),
                'hire_date': today - timedelta(days=420),
                'specialties': 'Hôtellerie, Immeubles de standing, Vitrerie',
            }
        )
        sup2_user.set_password('superviseur123')
        sup2_user.save()

        # Agents d'entretien
        agent1, _ = User.objects.get_or_create(
            username='agent',
            defaults={
                'first_name': 'Awa',
                'last_name': 'Faye',
                'email': 'awa.faye@cleanpro-services.com',
                'role': User.ROLE_AGENT,
                'phone': '+221 77 301 22 11',
                'job_title': 'Agente de Propreté Qualifiée',
                'monthly_salary': Decimal('165000'),
                'hourly_rate': Decimal('1500'),
                'hire_date': today - timedelta(days=365),
                'specialties': 'Bureaux, Sanitaires, Bio-nettoyage médical',
            }
        )
        agent1.set_password('agent123')
        agent1.save()

        other_agents_data = [
            ('ibrahima.fall', 'Ibrahima', 'Fall', '+221 77 889 12 34', 'Technicien Vitrerie & Travaux en hauteur', 195000, 'Vitrerie nacelle, Façades vitrées, Décapage'),
            ('mariama.ba', 'Mariama', 'Bâ', '+221 76 540 99 81', 'Agente d’entretien tertiaire', 155000, 'Entretien bureaux, Salles de conférence'),
            ('ousmane.gaye', 'Ousmane', 'Gaye', '+221 77 219 63 40', 'Machiniste (Autolaveuse & Monobrosse)', 185000, 'Cristallisation marbre, Autolaveuse industrielle'),
            ('khady.cisse', 'Khady', 'Cissé', '+221 78 441 09 22', 'Agente d’hygiène & Désinfection 3D', 170000, 'Désinfection, Dératisation, Cliniques'),
        ]
        agents_list = [agent1]
        for uname, fname, lname, phone, title, sal, spec in other_agents_data:
            ag, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'role': User.ROLE_AGENT,
                    'phone': phone,
                    'job_title': title,
                    'monthly_salary': Decimal(str(sal)),
                    'hourly_rate': Decimal('1500'),
                    'hire_date': today - timedelta(days=250),
                    'specialties': spec,
                }
            )
            ag.set_password('agent123')
            ag.save()
            agents_list.append(ag)

        # Compte Portail Client
        client_user, _ = User.objects.get_or_create(
            username='client',
            defaults={
                'first_name': 'Cheikh',
                'last_name': 'Sylla',
                'email': 'csylla@banque-atlantique.sn',
                'role': User.ROLE_CLIENT,
                'phone': '+221 33 849 10 00',
                'job_title': 'Responsable Moyens Généraux',
            }
        )
        client_user.set_password('client123')
        client_user.save()

        # 2. Équipes d'intervention
        team_alpha = Team.objects.create(
            name="Équipe Alpha - Tertiaire & Banques",
            supervisor=sup_user,
            vehicle="Fourgon Renault Master - DK-4582-AB",
            zone="Plateau / Almadies"
        )
        team_alpha.members.set([agent1, agents_list[2], agents_list[3]])

        team_beta = Team.objects.create(
            name="Équipe Bêta - Vitrerie, Chantiers & 3D",
            supervisor=sup2_user,
            vehicle="Pick-up Toyota Hilux - DK-9910-CD",
            zone="Zone Industrielle / Mermoz / Diamniadio"
        )
        team_beta.members.set([agents_list[1], agents_list[3], agents_list[4]])

        # 3. Clients & Sites
        c1 = Client.objects.create(
            user=client_user,
            name="Banque Atlantique - Siège Social",
            client_type=Client.TYPE_COMPANY,
            contact_person="M. Cheikh Sylla (Moyens Généraux)",
            phone="+221 33 849 10 00",
            email="moyens.generaux@banque-atlantique.sn",
            address="42 Avenue Léopold Sédar Senghor, Plateau",
            city="Dakar",
            tax_id="NINEA-00412589-2G2",
            notes="Exigence haute sécurité. Pointage obligatoire au poste de garde."
        )
        s1 = Site.objects.create(
            client=c1,
            name="Immeuble Siège Plateau (6 étages)",
            address="42 Avenue Léopold Sédar Senghor, Plateau",
            city="Dakar Plateau",
            surface_m2=2400,
            access_instructions="Badges visiteurs au R+0. Intervention avant 08h00 pour les agences.",
            contact_on_site="M. Cheikh Sylla",
            contact_phone="+221 77 500 11 22"
        )

        c2 = Client.objects.create(
            name="Clinique Pasteur & Laboratoires",
            client_type=Client.TYPE_MEDICAL,
            contact_person="Dr. Aminata Touré",
            phone="+221 33 860 45 45",
            email="intendance@clinique-pasteur.com",
            address="Corniche Ouest, Fann Résidence",
            city="Dakar",
            tax_id="NINEA-00785412-1M1",
            notes="Protocole bio-nettoyage hospitalier strict. Produits virucides homologués."
        )
        s2 = Site.objects.create(
            client=c2,
            name="Pôle Consultations & Bloc Analyses",
            address="Corniche Ouest, Fann Résidence",
            city="Dakar Fann",
            surface_m2=1150,
            access_instructions="Tenue EPI complète exigée (blouse, sur-chaussures, gants nitrile).",
            contact_on_site="Mme Ndèye Sarr (Surveillante Générale)",
            contact_phone="+221 77 611 33 44"
        )

        c3 = Client.objects.create(
            name="Syndic Résidence Les Almadies Plaza",
            client_type=Client.TYPE_SYNDIC,
            contact_person="M. Jean-Marc Gomis",
            phone="+221 33 820 90 00",
            email="syndic@almadies-plaza.sn",
            address="Route des Almadies, Ngor",
            city="Dakar",
            tax_id="NINEA-00963258-3B",
        )
        s3 = Site.objects.create(
            client=c3,
            name="Parties communes, Parking & Piscine (Tours A & B)",
            address="Route des Almadies",
            city="Almadies",
            surface_m2=3200,
            access_instructions="Clés local technique auprès du gardien chef.",
            contact_on_site="M. Abdoulaye Diouf (Syndic sur site)",
            contact_phone="+221 76 300 88 77"
        )

        c4 = Client.objects.create(
            name="Sénégal Logistique & Entrepôts (SLE)",
            client_type=Client.TYPE_INDUSTRIAL,
            contact_person="M. Karim Benjelloun",
            phone="+221 33 832 15 15",
            email="exploitation@sle-logistics.com",
            address="Zone Industrielle SODIDA, Lot 18",
            city="Dakar",
            tax_id="NINEA-00554120-9Z",
        )
        s4 = Site.objects.create(
            client=c4,
            name="Entrepôt Logistique & Bureaux Administratifs",
            address="Zone Industrielle SODIDA, Lot 18",
            city="Zone Industrielle",
            surface_m2=4500,
            access_instructions="Port du casque et chaussures de sécurité dans le hangar.",
            contact_on_site="M. Babacar Mbaye (Chef de Quai)",
            contact_phone="+221 77 910 20 30"
        )

        # 4. Contrats récurrents
        ctr1 = Contract.objects.create(
            reference="CTR-2026-001",
            client=c1,
            site=s1,
            title="Entretien quotidien des bureaux, guichets et vitrerie du Siège",
            frequency=Contract.FREQ_DAILY,
            monthly_amount_ht=Decimal('1450000'),
            start_date=today - timedelta(days=180),
            status=Contract.STATUS_ACTIVE,
            sla_description="Mise à disposition permanente de 4 agents du lundi au samedi + vitrerie mensuelle."
        )
        ctr2 = Contract.objects.create(
            reference="CTR-2026-002",
            client=c2,
            site=s2,
            title="Bio-nettoyage biquotidien et désinfection des salles de soins",
            frequency=Contract.FREQ_DAILY,
            monthly_amount_ht=Decimal('1100000'),
            start_date=today - timedelta(days=120),
            status=Contract.STATUS_ACTIVE,
            sla_description="Protocole hospitalier norme NF EN 14476, traçabilité par zone."
        )
        ctr3 = Contract.objects.create(
            reference="CTR-2026-003",
            client=c3,
            site=s3,
            title="Entretien hebdomadaire des halls, ascenseurs, marbres et parkings",
            frequency=Contract.FREQ_WEEKLY,
            monthly_amount_ht=Decimal('650000'),
            start_date=today - timedelta(days=90),
            status=Contract.STATUS_ACTIVE,
            sla_description="Passage 3 fois par semaine + cristallisation trimestrielle du hall en marbre."
        )

        # 5. Interventions (Passées, Aujourd'hui, Futures)
        int1 = Intervention.objects.create(
            code="INT-2026-001",
            title="Entretien matinal Siège Banque Atlantique (6 niveaux)",
            site=s1,
            contract=ctr1,
            intervention_type=Intervention.TYPE_REGULAR,
            team=team_alpha,
            scheduled_date=today,
            start_time="06:30",
            end_time="10:30",
            status=Intervention.STATUS_IN_PROGRESS,
            priority=Intervention.PRIORITY_HIGH,
            instructions="Attention particulière à la salle du Conseil au 5ème étage (réunion à 09h30).",
            check_in_time=timezone.now() - timedelta(hours=2)
        )
        int1.agents.set([agent1, agents_list[2], agents_list[3]])

        tasks_int1 = [
            ("Hall & Agence R+0", "Nettoyage et lustrage du sol granit + comptoirs clients", True),
            ("Bureaux Étages 1 à 4", "Dépoussiérage des postes informatiques et vidage corbeilles", True),
            ("Salle du Conseil (5ème)", "Aspiration moquette, désinfection table et mise en place", True),
            ("Blocs Sanitaires", "Désinfection complète et réassort savon / essuie-mains", False),
            ("Façade & Sas d'entrée", "Nettoyage sans traces des portes vitrées automatiques", False),
        ]
        for z, d, done in tasks_int1:
            ChecklistTask.objects.create(
                intervention=int1, zone_name=z, description=d, is_completed=done,
                completed_by=agent1 if done else None,
                completed_at=timezone.now() if done else None
            )

        int2 = Intervention.objects.create(
            code="INT-2026-002",
            title="Bio-nettoyage & Désinfection Pôle Consultations",
            site=s2,
            contract=ctr2,
            intervention_type=Intervention.TYPE_DISINFECTION,
            team=team_beta,
            scheduled_date=today,
            start_time="13:00",
            end_time="17:00",
            status=Intervention.STATUS_PLANNED,
            priority=Intervention.PRIORITY_URGENT,
            instructions="Utiliser le détergent-désinfectant Surfa'Safe Premium."
        )
        int2.agents.set([agents_list[4], agent1])
        for z, d in [
            ("Salles de prélèvement", "Désinfection des paillasses et fauteuils de prélèvement"),
            ("Salle d'attente", "Lavage virucide des sols et points de contact (poignées, chaises)"),
            ("Sanitaires Patients", "Détartrage acide et désinfection chlorée"),
        ]:
            ChecklistTask.objects.create(intervention=int2, zone_name=z, description=d)

        int3 = Intervention.objects.create(
            code="INT-2026-003",
            title="Décapage et Cristallisation Marbre Hall Tours A & B",
            site=s3,
            contract=ctr3,
            intervention_type=Intervention.TYPE_FLOOR,
            team=team_alpha,
            scheduled_date=today - timedelta(days=1),
            start_time="08:00",
            end_time="15:00",
            status=Intervention.STATUS_COMPLETED,
            priority=Intervention.PRIORITY_NORMAL,
            check_in_time=timezone.now() - timedelta(days=1, hours=7),
            check_out_time=timezone.now() - timedelta(days=1, hours=1),
            completion_notes="Brillance miroir obtenue sur les 450 m² du hall d'entrée. R.A.S.",
            client_rating=5,
            client_feedback="Excellent travail, le marbre a retrouvé son éclat d'origine."
        )
        int3.agents.set([agents_list[3], agents_list[2]])
        for z, d in [
            ("Hall Tour A", "Décapage monobrosse basse vitesse + aspiration eau"),
            ("Hall Tour B", "Cristallisation à la laine d'acier et lustrage haute vitesse"),
            ("Ascenseurs", "Polissage inox des cabines d'ascenseur"),
        ]:
            ChecklistTask.objects.create(intervention=int3, zone_name=z, description=d, is_completed=True, completed_by=sup_user)

        int4 = Intervention.objects.create(
            code="INT-2026-004",
            title="Nettoyage mécanisé autolaveuse Entrepôt 4500 m²",
            site=s4,
            intervention_type=Intervention.TYPE_DEEP,
            team=team_beta,
            scheduled_date=today + timedelta(days=1),
            start_time="08:00",
            end_time="16:00",
            status=Intervention.STATUS_PLANNED,
            priority=Intervention.PRIORITY_HIGH,
            instructions="Dégraissage mécanique des allées de circulation des chariots élévateurs."
        )
        int4.agents.set([agents_list[1], agents_list[3]])

        # 6. Contrôle Qualité
        QualityInspection.objects.create(
            intervention=int3,
            inspector=sup_user,
            score_cleanliness=96,
            score_protocol=94,
            score_punctuality=100,
            observations="Sols parfaitement cristallisés, balisage de sécurité bien respecté pendant le séchage.",
            client_signed=True,
            client_signatory_name="M. Abdoulaye Diouf (Syndic)"
        )

        # 7. Pointages & Congés
        for ag in agents_list:
            Attendance.objects.create(
                agent=ag,
                date=today,
                site=s1 if ag in [agent1, agents_list[2]] else s2,
                check_in="06:25",
                check_out="14:30",
                hours_worked=Decimal('8.0'),
                status=Attendance.STATUS_PRESENT,
                notes="À l'heure, tenue complète"
            )
        LeaveRequest.objects.create(
            agent=agents_list[2],
            leave_type=LeaveRequest.TYPE_ANNUAL,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=16),
            reason="Congé annuel familial à Saint-Louis",
            status=LeaveRequest.STATUS_PENDING
        )

        # 8. Stocks & Équipements
        items_data = [
            ("CHM-001", "Détergent Désinfectant Multi-surfaces Pin (Bidon 5L)", InventoryItem.CAT_CHEMICAL, 24, "Bidon 5L", 8, 9500, "Sénégal Chimie Pro"),
            ("CHM-002", "Virucide Hospitalier Surfa'Safe (Carton 12 sprays)", InventoryItem.CAT_CHEMICAL, 4, "Carton", 6, 42000, "BioMed Afrique"),
            ("CHM-003", "Produit Cristallisant Marbre & Pierre (Bidon 5L)", InventoryItem.CAT_CHEMICAL, 3, "Bidon 5L", 5, 28500, "Sénégal Chimie Pro"),
            ("CON-001", "Sacs Poubelles Haute Résistance 100L (Rouleau de 25)", InventoryItem.CAT_CONSUMABLE, 45, "Rouleau", 15, 3200, "Plastiques du Sahel"),
            ("CON-002", "Bobines Essuie-mains Papier Gaufré (Colis de 6)", InventoryItem.CAT_CONSUMABLE, 6, "Colis", 10, 14500, "Hygiène Plus Dakar"),
            ("EQP-001", "Autolaveuse Autoportée Kärcher B 90 R", InventoryItem.CAT_MACHINE, 2, "Machine", 1, 3850000, "Kärcher Center Dakar"),
            ("EQP-002", "Monobrosse Basse Vitesse Nilfisk + Plateau", InventoryItem.CAT_MACHINE, 4, "Machine", 1, 680000, "EquipPro Sénégal"),
            ("EPI-001", "Gants Nitrile Réutilisables Protection Chimique (Boîte 50)", InventoryItem.CAT_PPE, 12, "Boîte", 5, 7500, "SécuriTech"),
        ]
        created_items = []
        for sku, name, cat, qty, unit, thresh, cost, sup in items_data:
            it = InventoryItem.objects.create(
                sku=sku, name=name, category=cat,
                quantity=Decimal(str(qty)), unit=unit,
                min_threshold=Decimal(str(thresh)), unit_cost=Decimal(str(cost)),
                supplier=sup
            )
            created_items.append(it)

        StockMovement.objects.create(
            item=created_items[0],
            movement_type=StockMovement.MOVE_OUT,
            quantity=Decimal('4'),
            site=s1,
            performed_by=sup_user,
            notes="Dotation mensuelle Immeuble Banque Atlantique"
        )
        StockMovement.objects.create(
            item=created_items[1],
            movement_type=StockMovement.MOVE_OUT,
            quantity=Decimal('2'),
            site=s2,
            performed_by=sup2_user,
            notes="Urgence réassort Clinique Pasteur"
        )

        # 9. Devis & Factures (en FCFA, TVA 18%)
        q1 = Quote.objects.create(
            number="DEV-2026-001",
            client=c4,
            site_name="Entrepôt Logistique SODIDA (4 500 m²)",
            surface_m2=4500,
            service_description="Dégraissage industriel mécanisé des sols béton quartz + dépoussiérage charpente métallique.",
            amount_ht=Decimal('850000'),
            tax_rate=Decimal('18.00'),
            issue_date=today - timedelta(days=5),
            valid_until=today + timedelta(days=25),
            status=Quote.STATUS_SENT
        )
        q2 = Quote.objects.create(
            number="DEV-2026-002",
            client=c1,
            site_name="Nettoyage vitrerie grande hauteur (Façade principale)",
            surface_m2=1200,
            service_description="Lavage des façades vitrées par nacelle élévatrice et perche eau pure (forfait trimestriel).",
            amount_ht=Decimal('550000'),
            tax_rate=Decimal('18.00'),
            issue_date=today - timedelta(days=12),
            valid_until=today + timedelta(days=18),
            status=Quote.STATUS_ACCEPTED
        )

        inv1 = Invoice.objects.create(
            number="FAC-2026-001",
            client=c1,
            contract=ctr1,
            period_label="Redevance mensuelle d'entretien - Octobre 2026",
            issue_date=today - timedelta(days=10),
            due_date=today + timedelta(days=5),
            amount_ht=Decimal('1450000'),
            tax_rate=Decimal('18.00'),
            amount_paid=Decimal('1711000'),
            status=Invoice.STATUS_PAID,
            payment_method=Invoice.METHOD_TRANSFER
        )
        InvoiceLine.objects.create(
            invoice=inv1,
            description="Forfait mensuel d'entretien ménager Siège Plateau (6 étages - 4 agents permanents)",
            quantity=Decimal('1.0'),
            unit_price=Decimal('1450000')
        )

        inv2 = Invoice.objects.create(
            number="FAC-2026-002",
            client=c2,
            contract=ctr2,
            period_label="Bio-nettoyage hospitalier - Octobre 2026",
            issue_date=today - timedelta(days=5),
            due_date=today + timedelta(days=10),
            amount_ht=Decimal('1100000'),
            tax_rate=Decimal('18.00'),
            amount_paid=Decimal('600000'),
            status=Invoice.STATUS_PARTIAL,
            payment_method=Invoice.METHOD_CHECK
        )
        InvoiceLine.objects.create(
            invoice=inv2,
            description="Prestation mensuelle de bio-nettoyage et désinfection (Pôle Consultations & Labo)",
            quantity=Decimal('1.0'),
            unit_price=Decimal('1100000')
        )

        inv3 = Invoice.objects.create(
            number="FAC-2026-003",
            client=c3,
            contract=ctr3,
            period_label="Entretien parties communes & Cristallisation marbre - Octobre 2026",
            issue_date=today - timedelta(days=2),
            due_date=today + timedelta(days=13),
            amount_ht=Decimal('650000'),
            tax_rate=Decimal('18.00'),
            amount_paid=Decimal('0'),
            status=Invoice.STATUS_UNPAID,
            payment_method=Invoice.METHOD_MOBILE
        )
        InvoiceLine.objects.create(
            invoice=inv3,
            description="Forfait mensuel parties communes Résidence Les Almadies Plaza (Tours A & B)",
            quantity=Decimal('1.0'),
            unit_price=Decimal('650000')
        )

        self.stdout.write(self.style.SUCCESS("Données de démonstration CleanPro ERP créées avec succès !"))
