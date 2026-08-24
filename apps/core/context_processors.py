from django.db.models import Q


def passamoz_ui(request):
    """Small global UI context used by the app shell."""
    unread_count = 0
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        # Import lazily so this processor never blocks Django startup.
        from apps.notifications.models import Notification
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {"passamoz_unread_count": unread_count}
