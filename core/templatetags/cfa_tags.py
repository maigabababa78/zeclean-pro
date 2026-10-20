import re
from urllib.parse import quote
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def fcfa(value):
    """Formate un montant en Francs CFA avec séparateur de milliers par espace (ex: 450 000 FCFA)."""
    try:
        amount = int(round(float(value or 0)))
        formatted = f"{amount:,}".replace(",", " ")
        return f"{formatted} FCFA"
    except (ValueError, TypeError):
        return f"{value} FCFA"


@register.filter
def fcfa_num(value):
    """Formate un nombre avec séparateur de milliers sans le suffixe FCFA."""
    try:
        amount = int(round(float(value or 0)))
        return f"{amount:,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)


def _clean_phone(phone_str):
    digits = re.sub(r'\D', '', str(phone_str or ''))
    if not digits:
        return '221770000000'
    if len(digits) == 9 and digits[0] in ('7', '3'):
        return f"221{digits}"
    return digits


@register.filter
def whatsapp_invoice_url(invoice):
    """Génère le lien WhatsApp pré-rempli pour envoyer une facture ou relance au client."""
    company = getattr(settings, 'COMPANY_NAME', 'ZeClean Pro SARL')
    phone = _clean_phone(invoice.client.phone)
    ttc = f"{int(invoice.amount_ttc):,}".replace(",", " ")
    reste = f"{int(invoice.balance_due):,}".replace(",", " ")
    if invoice.balance_due > 0:
        msg = (
            f"Bonjour {invoice.client.contact_person} ({invoice.client.name}),\n\n"
            f"Voici le récapitulatif de votre facture *{invoice.number}* ({company}) :\n"
            f"• Objet : {invoice.period_label}\n"
            f"• Montant TTC : *{ttc} FCFA*\n"
            f"• Reste à régler : *{reste} FCFA*\n"
            f"• Échéance : {invoice.due_date.strftime('%d/%m/%Y')}\n\n"
            f"Merci pour votre confiance. Vous pouvez régler par Virement, Chèque ou Wave / Orange Money."
        )
    else:
        msg = (
            f"Bonjour {invoice.client.contact_person} ({invoice.client.name}),\n\n"
            f"Nous vous confirmons la bonne réception du règlement intégral de votre facture *{invoice.number}* "
            f"d'un montant de *{ttc} FCFA*.\n\n"
            f"Toute l'équipe {company} vous remercie pour votre confiance !"
        )
    return f"https://wa.me/{phone}?text={quote(msg)}"


@register.filter
def whatsapp_quote_url(q):
    """Génère le lien WhatsApp pré-rempli pour envoyer une proposition de devis au client."""
    company = getattr(settings, 'COMPANY_NAME', 'ZeClean Pro SARL')
    phone = _clean_phone(q.client.phone)
    ttc = f"{int(q.amount_ttc):,}".replace(",", " ")
    msg = (
        f"Bonjour {q.client.contact_person} ({q.client.name}),\n\n"
        f"Suite à votre demande, veuillez trouver notre proposition commerciale *{q.number}* ({company}) :\n"
        f"• Site : {q.site_name} ({q.surface_m2} m²)\n"
        f"• Prestation : {q.service_description}\n"
        f"• Montant Total TTC : *{ttc} FCFA*\n"
        f"• Validité : jusqu'au {q.valid_until.strftime('%d/%m/%Y')}\n\n"
        f"Restant à votre entière disposition pour démarrer l'intervention dès votre validation."
    )
    return f"https://wa.me/{phone}?text={quote(msg)}"


@register.filter
def whatsapp_intervention_client_url(inter):
    """Génère un lien WhatsApp pour notifier le client de l'intervention ou du rapport qualité."""
    company = getattr(settings, 'COMPANY_NAME', 'ZeClean Pro SARL')
    phone = _clean_phone(inter.site.contact_phone or inter.site.client.phone)
    msg = (
        f"Bonjour {inter.site.contact_on_site or inter.site.client.contact_person},\n\n"
        f"Point d'information *{company}* concernant l'intervention *{inter.code}* :\n"
        f"• Mission : {inter.title}\n"
        f"• Site : {inter.site.name}\n"
        f"• Date & Créneau : {inter.scheduled_date.strftime('%d/%m/%Y')} ({inter.start_time.strftime('%H:%M')} - {inter.end_time.strftime('%H:%M')})\n"
        f"• Statut : *{inter.get_status_display()}* (Checklist : {inter.checklist_progress}%)\n\n"
        f"Cordialement, le service supervision."
    )
    return f"https://wa.me/{phone}?text={quote(msg)}"


@register.filter
def whatsapp_agent_mission_url(agent):
    """Génère un lien WhatsApp direct vers un collaborateur."""
    company = getattr(settings, 'COMPANY_NAME', 'ZeClean Pro SARL')
    phone = _clean_phone(agent.phone)
    msg = (
        f"Bonjour {agent.get_full_name()},\n"
        f"Message de la supervision *{company}* concernant votre planning d'intervention. "
        f"Merci de consulter votre espace agent ou de confirmer votre prise de poste."
    )
    return f"https://wa.me/{phone}?text={quote(msg)}"
