from django.conf import settings


def company_context(request):
    return {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'ZeClean Pro SARL'),
        'COMPANY_PHONE': getattr(settings, 'COMPANY_PHONE', '+221 33 800 00 00'),
        'COMPANY_EMAIL': getattr(settings, 'COMPANY_EMAIL', 'contact@zeclean-pro.com'),
        'COMPANY_ADDRESS': getattr(settings, 'COMPANY_ADDRESS', 'Avenue Jean-Paul II, Zone Industrielle'),
        'COMPANY_RC': getattr(settings, 'COMPANY_RC', 'RC-DKR-2026-B-14520'),
        'COMPANY_NINEA': getattr(settings, 'COMPANY_NINEA', 'NINEA-008451236'),
        'DEFAULT_CURRENCY': getattr(settings, 'DEFAULT_CURRENCY', 'FCFA'),
        'DEFAULT_TVA_RATE': getattr(settings, 'DEFAULT_TVA_RATE', 18.0),
    }
