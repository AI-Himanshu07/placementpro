from .models import Notification

def global_notifications(request):
    try:
        notes = Notification.objects.all().order_by('-id')[:5]
    except:
        notes = []

    return {
        'global_notifications': notes
    }