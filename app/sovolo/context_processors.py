from django.conf import settings

def google_analytics(request):
    prop_id = settings.GOOGLE_ANALYTICS_PROP
    return {"GOOGLE_ANALYTICS_PROP": prop_id}
