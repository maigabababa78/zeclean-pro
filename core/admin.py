from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Team, Client, Site, Contract, Intervention,
    ChecklistTask, QualityInspection, Attendance, LeaveRequest,
    InventoryItem, StockMovement, Quote, Invoice, InvoiceLine
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'phone', 'job_title', 'is_available')
    list_filter = ('role', 'is_available')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations Métier Nettoyage', {
            'fields': ('role', 'phone', 'job_title', 'hourly_rate', 'monthly_salary', 'hire_date', 'specialties', 'is_available')
        }),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor', 'zone', 'vehicle')
    filter_horizontal = ('members',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_type', 'contact_person', 'phone', 'city', 'is_active')
    list_filter = ('client_type', 'city', 'is_active')
    search_fields = ('name', 'contact_person', 'phone', 'email')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'city', 'surface_m2', 'contact_on_site')
    list_filter = ('city',)
    search_fields = ('name', 'client__name', 'address')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'site', 'frequency', 'monthly_amount_ht', 'status', 'start_date')
    list_filter = ('status', 'frequency')


class ChecklistTaskInline(admin.TabularInline):
    model = ChecklistTask
    extra = 1


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'site', 'intervention_type', 'scheduled_date', 'start_time', 'status', 'priority')
    list_filter = ('status', 'intervention_type', 'priority', 'scheduled_date')
    inlines = [ChecklistTaskInline]


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = ('intervention', 'inspector', 'score_cleanliness', 'score_protocol', 'score_punctuality', 'client_signed', 'inspected_at')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('agent', 'date', 'site', 'check_in', 'check_out', 'hours_worked', 'status')
    list_filter = ('status', 'date')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('agent', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'quantity', 'unit', 'min_threshold', 'unit_cost')
    list_filter = ('category',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('item', 'movement_type', 'quantity', 'site', 'performed_by', 'created_at')
    list_filter = ('movement_type',)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'site_name', 'amount_ht', 'status', 'issue_date')
    list_filter = ('status',)


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'period_label', 'amount_ht', 'amount_paid', 'status', 'due_date')
    list_filter = ('status', 'payment_method')
    inlines = [InvoiceLineInline]
